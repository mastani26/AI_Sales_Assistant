import pandas as pd
import random
from faker import Faker

fake = Faker()

# Indian first and last names
indian_first_names = ["Aarav", "Vivaan", "Aditya", "Krishna", "Arjun", "Riya", "Ananya", "Isha", "Kavya", "Meera"]
indian_last_names = ["Sharma", "Verma", "Reddy", "Iyer", "Patel", "Gupta", "Kumar", "Das", "Nair", "Chopra"]

# Product list
products = [
    "Cosmetic Care", "Home Essentials", "Electronics", "Groceries",
    "Clothing", "Sports Gear", "Furniture", "Books", "Toys", "Kitchenware"
]

# Feedback examples with linked sentiments
feedback_map = {
    "Asked for discount": "Neutral",
    "Happy with product": "Positive",
    "Interested in EMI option": "Neutral",
    "Had issue with delivery": "Negative",
    "Requested callback": "Neutral",
    "Price too high": "Negative",
    "Wants bulk purchase": "Positive",
    "Positive response": "Positive",
    "Not interested right now": "Negative"
}

def generate_name():
    return f"{random.choice(indian_first_names)} {random.choice(indian_last_names)}"

def generate_phone():
    return f"+91{random.randint(6000000000, 9999999999)}"

def generate_date():
    return fake.date_between(start_date="-2y", end_date="today")

# Dictionary to keep track of previous purchases for each email
purchase_history = {}

data = []
for i in range(500):  # 500 people
    name = generate_name()
    email = f"{name.lower().replace(' ', '')}{i}@email.com"
    phone = generate_phone()
    product = random.choice(products)
    invoice = f"INV{1000+i}"
    date = generate_date()
    feedback = random.choice(list(feedback_map.keys()))
    sentiment = feedback_map[feedback]

    # If first time, pre-populate 1–3 random purchases
    if email not in purchase_history:
        previous = random.sample(products, k=random.randint(1, 3))
        purchase_history[email] = previous.copy()

    # Add current purchase to history
    prev_purchases = purchase_history[email]
    purchase_history[email].append(product)

    # Store row (latest product + all previous purchases before this one)
    data.append([
        name, email, phone, product, invoice, date, feedback, sentiment,
        ", ".join(prev_purchases) if prev_purchases else "None"
    ])

df = pd.DataFrame(data, columns=[
    "Name", "Email", "Phone", "Product",
    "Invoice", "Date of Purchase", "Call Feedback", "Sentiment",
    "Previous Purchases"
])

df.to_excel("crm_data.xlsx", index=False)
print("✅ CRM data with populated Previous Purchases column generated successfully in crm_data.xlsx")
