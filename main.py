from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from collections import defaultdict
from datetime import datetime
import os
import pandas as pd
import shutil
import tempfile

# Google Sheets
import gspread
from google.oauth2.service_account import Credentials

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# In-memory history + analytics
conversation_history = []
sentiment_counts = defaultdict(int)

# Prompt template for sentiment
SENTIMENT_PROMPT = """
You are a sentiment detection engine.
Analyze the following text and respond in this exact format:

Sentiment: Positive / Negative / Neutral
Tone: Friendly / Upset / Angry / Polite / Neutral
Explanation: Short plain explanation

Text: "{}"
"""

# ---------------- GOOGLE SHEETS SETUP ---------------- #
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("cred.json", scopes=SCOPES)
gs_client = gspread.authorize(creds)

# Sheet 1: Conversation transcript logging
SHEET_ID = "1v0zVvH1nF4O-Kxr-WA91_Xj-vdOHsdQ7AS8iaSCsPvM"
sheet = gs_client.open_by_key(SHEET_ID).sheet1

# Sheet 2: AI Response logging
SHEET2_ID = "1eattCsIt1yytAWgc8I3qWfqIuJ3cQYY_3jYsmaBYOhE"
sheet_ai = gs_client.open_by_key(SHEET2_ID).sheet1
# ----------------------------------------------------- #

CRM_FILE = "crm_data.xlsx"  # Your CRM file

def parse_result(result: str):
    """Extract Sentiment, Tone, and Explanation from LLM output."""
    sentiment, tone, explanation = "Neutral", "Neutral", ""
    for line in result.split("\n"):
        if line.lower().startswith("sentiment"):
            sentiment = line.split(":", 1)[1].strip()
        elif line.lower().startswith("tone"):
            tone = line.split(":", 1)[1].strip()
        elif line.lower().startswith("explanation"):
            explanation = line.split(":", 1)[1].strip()
    return sentiment, tone, explanation


# ---------------- RECOMMENDATION HELPER ---------------- #
def generate_recommendation(product: str):
    """Generate complementary product recommendations instead of repeating same product."""
    product_lower = product.lower()

    mapping = {
        "bag": ("Travel Pillow", "Since the customer bought a Bag, a Travel Pillow could be useful for comfort."),
        "grocer": ("Snacks & Beverages", "Groceries often pair with snacks or beverages that customers may enjoy."),
        "home essentials": ("Cleaning Supplies", "Home essentials buyers might also need reliable cleaning products."),
        "kitchen": ("Cookware Set", "Kitchenware customers may also be interested in advanced cookware."),
        "laptop": ("Laptop Bag", "Since they purchased a Laptop, a protective Laptop Bag could be helpful."),
        "phone": ("Phone Case", "A Phone purchase often goes with a protective Case."),
        "tablet": ("Tablet Stand", "A Tablet Stand could improve usability for a Tablet buyer."),
        "shoes": ("Shoe Cleaner", "Customers buying Shoes may also want Shoe Cleaner or Care Kits.")
    }

    for key, (rec_name, rec_desc) in mapping.items():
        if key in product_lower:
            return rec_name, rec_desc

    # Default fallback
    return "Gift Voucher", f"A gift voucher could be a nice add-on for {product} buyers."


# ---------------- AUDIO TRANSCRIPTION ---------------- #
@app.post("/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):
    """Receive audio file, transcribe it, detect sentiment."""
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[1] or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        # Transcribe using Groq Whisper
        with open(temp_file_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f
            )

        text = transcription.text.strip()
        if not text:
            text = "No transcription."

        # Sentiment detection
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": SENTIMENT_PROMPT.format(text)}],
            temperature=0
        )
        sentiment = response.choices[0].message.content.strip()

        # Clean up temp file
        os.remove(temp_file_path)

        return {"text": text, "sentiment": sentiment}

    except Exception as e:
        return {"text": "No transcription.", "sentiment": "Neutral", "error": str(e)}


# ---------------- CRM ---------------- #
@app.post("/get_customer")
async def get_customer(data: dict):
    """Fetch customer details from CRM by email or phone."""
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip().replace(" ", "").replace("-", "")
    if not email and not phone:
        return {"error": "Email or phone is required"}, 400
    try:
        df = pd.read_excel(CRM_FILE)

        # Lookup by email first
        customer = None
        if email:
            customer_row = df[df["Email"].str.lower().str.strip() == email]
            if not customer_row.empty:
                customer = customer_row.iloc[0].to_dict()
        # Lookup by phone if email not found or not provided
        if not customer and phone:
            df["PhoneClean"] = df["Phone"].astype(str).str.replace(" ", "").str.replace("-", "")
            customer_row = df[df["PhoneClean"] == phone]
            if not customer_row.empty:
                customer = customer_row.iloc[0].to_dict()

        if not customer:
            return {"error": "Customer not found"}, 404

        # Return all fields frontend needs
        customer_data = {
            "Name": customer.get("Name", "Unknown"),
            "Product": customer.get("Product", "—"),
            "Email": customer.get("Email", "—"),
            "Phone": customer.get("Phone", "—"),
            "Query": customer.get("Call Feedback", "—"),
            "PreviousPurchases": customer.get("Previous Purchases", "—"),
            "Notes": customer.get("Notes", "—"),
        }
        return customer_data
    except Exception as e:
        return {"error": str(e)}, 500


# ---------------- AI RESPONSE ---------------- #
@app.post("/analyze-text")
async def analyze_text(data: dict):
    """Fetch query from CRM if not provided and generate AI response."""
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip().replace(" ", "").replace("-", "")
    text = data.get("text", "").strip()

    if not email and not phone:
        return {"error": "Email or phone is required"}, 400

    try:
        df = pd.read_excel(CRM_FILE)

        # Lookup by email or phone
        customer_row = None
        if email:
            customer_row = df[df["Email"].str.lower().str.strip() == email]
        if (customer_row is None or customer_row.empty) and phone:
            df["PhoneClean"] = df["Phone"].astype(str).str.replace(" ", "").str.replace("-", "")
            customer_row = df[df["PhoneClean"] == phone]
        if customer_row.empty:
            return {"error": "Customer not found"}, 404

        customer_info = customer_row.iloc[0].to_dict()

        # Use stored Call Feedback if text is empty
        if not text:
            text = customer_info.get("Call Feedback", "")
        if not text:
            text = "No query provided by customer."

        # Construct AI prompt
        customer_text = f"Customer Name: {customer_info['Name']}, Product: {customer_info['Product']}"
        PROMPT = f"""
        You are a polite, soft, friendly AI Sales Assistant.
        {customer_text}
        Customer Query: "{text}"
        Respond in a helpful, soft, friendly, and polite manner.
        """

        # Sentiment detection
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": SENTIMENT_PROMPT.format(text)}],
            temperature=0
        )
        sentiment, tone, explanation = parse_result(response.choices[0].message.content.strip())

        # Generate AI response
        ai_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": PROMPT}],
            temperature=0.7
        ).choices[0].message.content.strip()

        # Product Recommendations based on previous purchases
        prev_products = customer_info.get("Previous Purchases", "")
        recommendations = []
        if prev_products and prev_products != "—":
            prev_list = [p.strip() for p in prev_products.split(",")]
            for p in prev_list:
                rec_name, rec_desc = generate_recommendation(p)
                recommendations.append({
                    "name": rec_name,
                    "desc": rec_desc
                })

        timestamp = datetime.now().strftime("%d/%m/%Y, %I:%M:%S %p")

        return_data = {
            "Name": customer_info.get("Name", "Unknown"),
            "Product": customer_info.get("Product", "—"),
            "Email": customer_info.get("Email", "—"),
            "Phone": customer_info.get("Phone", "—"),
            "Query": text,
            "ai_response": ai_response,
            "sentiment": sentiment,
            "tone": tone,
            "explanation": explanation,
            "timestamp": timestamp,
            "Recommendations": recommendations
        }

        # Log to conversation sheet
        sheet.append_row([text, sentiment, tone, timestamp])

        # Log to AI response sheet
        sheet_ai.append_row([
            customer_info.get("Name", ""),
            customer_info.get("Email", ""),
            text,
            ai_response,
            timestamp
        ])

        # Save history & analytics
        conversation_history.append(return_data)
        sentiment_counts[sentiment] += 1

        return return_data

    except Exception as e:
        return {"error": str(e)}


# ---------------- POST-CALL SUMMARY ---------------- #
@app.post("/generate-summary")
async def generate_summary(payload: dict):
    transcript = payload.get("transcript", "")

    if not transcript.strip():
        return {"summary": "No transcript provided."}

    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Force the model to output a structured summary
        prompt = f"""
You are an AI assistant that generates professional **Post-Call Summaries**.

Transcript:
{transcript}

Format the summary exactly like this:

Post-Call Summary: [Customer Name] ([Customer ID])  
Date of Call: [Insert Date of Call Here]  
Customer: [Customer Name] ([Customer ID]) - [Industry]  
Overall Sentiment: [Brief Sentiment Analysis]  
Key Topics:  
- Budget: [Budget Info]  
- Phone Requirements: [Requirements Info]  
- Battery Life: [Battery-related Info]  
- Previous Purchases: [Mention past purchases if available]

Now generate the Post-Call Summary based only on the transcript provided.
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for call center summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500,
        )

        summary_text = response.choices[0].message.content.strip()


        if not summary_text:
            summary_text = "No summary generated."

        return {"summary": summary_text}

    except Exception as e:
        return {"summary": f"Error generating summary: {str(e)}"}



# ---------------- HISTORY & ANALYTICS ---------------- #
@app.get("/history")
async def get_history():
    return conversation_history

@app.get("/analytics")
async def get_analytics():
    total = sum(sentiment_counts.values())
    return {
        "total": total,
        "distribution": dict(sentiment_counts)
    }
