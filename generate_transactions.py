import pandas as pd
import random
import uuid
from faker import Faker
from datetime import datetime, timedelta
import numpy as np
import json
from collections import defaultdict

# Load transaction parameters from config file
with open("transaction_parameters.json", "r") as f:
    config = json.load(f)

# Initialize Faker
fake = Faker()

# Extract parameters from config
num_transactions = config["num_transactions"]
num_customers = config["num_customers"]
max_transactions_per_card = config["max_transactions_per_card"]
max_cards_per_customer = config["max_cards_per_customer"]
transaction_period_days = config["transaction_period_days"]
alpha = config["transaction_amount_distribution"]["alpha"]
beta = config["transaction_amount_distribution"]["beta"]
max_transactions_per_card_per_day = config["max_transactions_per_card_per_day"]
max_transactions_per_customer_per_day = config["max_transactions_per_customer_per_day"]

# Generate Customers, Cards, Customer Names, and Card Issuers
customers = [str(uuid.uuid4()) for _ in range(num_customers)]
customer_cards = {customer: [str(uuid.uuid4()) for _ in range(random.randint(1, max_cards_per_customer))] for customer in customers}

# Map each customer ID to a unique name
customer_names = {customer: fake.name() for customer in customers}

# Map each card ID to a unique issuer
possible_issuers = ["Bank of America", "Chase", "Wells Fargo", "CitiBank"]
card_issuers = {card: random.choice(possible_issuers) for cards in customer_cards.values() for card in cards}

# Dictionary to store consistent merchant information for each unique merchant_id
merchants = {}

# Dictionary to track the number of transactions per card and per customer per day
transactions_per_card_per_day = defaultdict(lambda: defaultdict(int))
transactions_per_customer_per_day = defaultdict(lambda: defaultdict(int))

# Generate transaction datetime within a specified period
def generate_transaction_datetime():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=transaction_period_days)
    return fake.date_time_between(start_date=start_date, end_date=end_date)

# Generate transaction amount following a gamma distribution
def generate_transaction_amount():
    return round(np.random.gamma(alpha, beta), 2)

# Generate a DataFrame of transactions
def generate_transactions(n):
    data = []
    for _ in range(n):
        customer = random.choice(customers)
        card = random.choice(customer_cards[customer])
        
        # Generate a transaction date
        transaction_date = generate_transaction_datetime()
        transaction_date_str = transaction_date.strftime("%Y-%m-%d")
        
        # Check daily limits for the card and customer
        if transactions_per_card_per_day[card][transaction_date_str] >= max_transactions_per_card_per_day:
            continue
        if transactions_per_customer_per_day[customer][transaction_date_str] >= max_transactions_per_customer_per_day:
            continue
        
        # Ensure the max transactions per card limit is respected
        card_transaction_count = len([t for t in data if t["card_id"] == card])
        if card_transaction_count >= max_transactions_per_card:
            continue

        # Generate a merchant ID and check if it exists in merchants dictionary
        merchant_id = str(uuid.uuid4())
        if merchant_id not in merchants:
            # Generate new merchant details if not in dictionary
            merchants[merchant_id] = {
                "merchant_name": fake.company(),
                "merchant_location": {
                    "city": fake.city(),
                    "state": fake.state_abbr(),
                    "country": fake.country_code()
                },
                "merchant_terminal_id": "T" + str(random.randint(1000, 9999))
            }
        
        # Retrieve merchant details from the dictionary
        merchant_details = merchants[merchant_id]
        
        # Determine account type and corresponding card type
        account_type = random.choice(["debit", "credit", "saving"])
        if account_type == "debit":
            card_type = "Visa"
        elif account_type == "credit":
            card_type = random.choice(["Visa", "MasterCard"])
        elif account_type == "saving":
            card_type = "Visa"
        
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "customer_id": customer,
            "card_id": card,
            "transaction_type": random.choice(["debit_card", "credit_card", "online_banking", "mobile_app"]),
            "transaction_date_time": transaction_date,
            "transaction_amount": generate_transaction_amount(),
            "currency": random.choice(["USD", "EUR", "GBP", "JPY", "CAD"]),
            "mcc": random.choice(["5411", "5812", "5921", "5999", "5735"]),
            "description": random.choice(["Grocery", "Restaurant", "Electronics", "Clothing", "Gas"]),
            "account_type": account_type,  # Set account type
            "account_balance": round(random.uniform(100.0, 10000.0), 2),
            "card_type": card_type,  # Set card type based on account type
            "card_number_masked": "**** **** **** " + str(random.randint(1000, 9999)),
            "card_expiration_date": fake.credit_card_expire(),
            "card_issuer": card_issuers[card],  # Use the pre-generated card issuer
            "cardholder_name": customer_names[customer],  # Use the pre-generated customer name
            "merchant_id": merchant_id,
            "merchant_name": merchant_details["merchant_name"],
            "merchant_location": merchant_details["merchant_location"],
            "merchant_terminal_id": merchant_details["merchant_terminal_id"],
            "payment_method": random.choice(["chip", "NFC", "swipe"]),
            "payment_channel": random.choice(["POS", "online", "mobile_app"]),
            "geolocation": {
                "latitude": fake.latitude(),
                "longitude": fake.longitude()
            },
            "authorization_code": str(random.randint(100000, 999999)),
            "authentication_method": random.choice(["PIN", "biometric", "password"]),
            "3d_secure_status": random.choice(["Passed", "Failed"]),
            "fraud_risk_score": random.randint(0, 100),
            "transaction_status": random.choice(["approved", "pending", "failed"]),
            "failure_reason": random.choice(["insufficient funds", "fraud detected", "technical error", None]),
            "exchange_rate": round(random.uniform(0.5, 1.5), 2) if random.choice([True, False]) else None,
            "rewards_earned": random.randint(0, 10),
            "ip_address": fake.ipv4(),
            "device_id": str(uuid.uuid4()),
            "user_agent": fake.user_agent(),
            "session_id": str(uuid.uuid4()),
            "referral_source": random.choice(["email", "social media", "direct", "referral"])
        }
        
        # Update daily transaction counts
        transactions_per_card_per_day[card][transaction_date_str] += 1
        transactions_per_customer_per_day[customer][transaction_date_str] += 1
        
        data.append(transaction)
    
    df = pd.DataFrame(data)
    return df

# Generate the transactions DataFrame
df = generate_transactions(num_transactions)
df.head()
