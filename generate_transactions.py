import pandas as pd
import random
import uuid
from faker import Faker
from datetime import datetime, timedelta
import numpy as np
import json

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

# Generate Customers and Cards
customers = [str(uuid.uuid4()) for _ in range(num_customers)]
customer_cards = {customer: [str(uuid.uuid4()) for _ in range(random.randint(1, max_cards_per_customer))] for customer in customers}

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
        
        # Ensure the max transactions per card limit is respected
        card_transaction_count = len([t for t in data if t["card_id"] == card])
        if card_transaction_count >= max_transactions_per_card:
            continue
        
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "customer_id": customer,
            "card_id": card,
            "transaction_type": random.choice(["debit_card", "credit_card", "online_banking", "mobile_app"]),
            "transaction_date_time": generate_transaction_datetime(),
            "transaction_amount": generate_transaction_amount(),
            "currency": random.choice(["USD", "EUR", "GBP", "JPY", "CAD"]),
            "mcc": random.choice(["5411", "5812", "5921", "5999", "5735"]),
            "description": random.choice(["Grocery", "Restaurant", "Electronics", "Clothing", "Gas"]),
            "account_type": random.choice(["savings", "checking", "credit"]),
            "account_balance": round(random.uniform(100.0, 10000.0), 2),
            "card_type": random.choice(["Visa", "MasterCard", "Amex"]),
            "card_number_masked": "**** **** **** " + str(random.randint(1000, 9999)),
            "card_expiration_date": fake.credit_card_expire(),
            "card_issuer": random.choice(["Bank of America", "Chase", "Wells Fargo", "CitiBank"]),
            "cardholder_name": fake.name(),
            "merchant_id": str(uuid.uuid4()),
            "merchant_name": fake.company(),
            "merchant_location": {
                "city": fake.city(),
                "state": fake.state_abbr(),
                "country": fake.country_code()
            },
            "merchant_terminal_id": "T" + str(random.randint(1000, 9999)),
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
        data.append(transaction)
    
    df = pd.DataFrame(data)
    return df

# Generate the transactions DataFrame
df = generate_transactions(num_transactions)
df.head()
