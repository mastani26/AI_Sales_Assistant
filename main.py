from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from collections import defaultdict
from datetime import datetime
import os

# Google Sheets imports
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

# Updated Prompt template
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

SHEET_ID = "1v0zVvH1nF4O-Kxr-WA91_Xj-vdOHsdQ7AS8iaSCsPvM"  # 🔹 Replace with your Google Sheet ID
sheet = gs_client.open_by_key(SHEET_ID).sheet1
# ----------------------------------------------------- #


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


@app.post("/analyze-text")
async def analyze_text(data: dict):
    text = data.get("text", "").strip()
    if not text:
        return {"text": "", "sentiment": "Neutral", "tone": "Neutral", "explanation": "No text provided."}

    try:
        # Sentiment detection using Groq LLaMA
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": SENTIMENT_PROMPT.format(text)}],
            temperature=0
        )
        result = response.choices[0].message.content.strip()

        sentiment, tone, explanation = parse_result(result)
        timestamp = datetime.now().strftime("%d/%m/%Y, %I:%M:%S %p")

        return_data = {
            "text": text,
            "sentiment": sentiment,
            "tone": tone,
            "explanation": explanation,
            "timestamp": timestamp
        }

        # Save history & analytics
        conversation_history.append(return_data)
        sentiment_counts[sentiment] += 1

        # ✅ Save to Google Sheets
        sheet.append_row([
            return_data["text"],        # Transcript
            return_data["sentiment"],   # Sentiment
            return_data["tone"],        # Tone
            return_data["timestamp"]    # Date
        ])

        return return_data

    except Exception as e:
        return {"text": text, "sentiment": "Error", "tone": "Error", "explanation": str(e)}


@app.post("/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):
    try:
        # Save audio temp file
        contents = await file.read()
        temp_file = "temp_audio.webm"
        with open(temp_file, "wb") as f:
            f.write(contents)

        # Transcribe using Whisper
        with open(temp_file, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="en"
            )
        text = transcription.text.strip()

        if not text:
            return {"text": "", "sentiment": "Neutral", "tone": "Neutral", "explanation": "No speech detected."}

        # Sentiment detection
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": SENTIMENT_PROMPT.format(text)}],
            temperature=0
        )
        result = response.choices[0].message.content.strip()

        sentiment, tone, explanation = parse_result(result)
        timestamp = datetime.now().strftime("%d/%m/%Y, %I:%M:%S %p")

        return_data = {
            "text": text,
            "sentiment": sentiment,
            "tone": tone,
            "explanation": explanation,
            "timestamp": timestamp
        }

        # Save history & analytics
        conversation_history.append(return_data)
        sentiment_counts[sentiment] += 1

        # ✅ Save to Google Sheets
        sheet.append_row([
            return_data["text"],        # Transcript
            return_data["sentiment"],   # Sentiment
            return_data["tone"],        # Tone
            return_data["timestamp"]    # Date
        ])

        return return_data

    except Exception as e:
        return {"text": "", "sentiment": "Error", "tone": "Error", "explanation": str(e)}


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
