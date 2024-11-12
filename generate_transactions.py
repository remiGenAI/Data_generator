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
max_merchants = config["max_merchants"]
domestic_percentage = config["domestic_percentage"]

# Generate Customers, Cards, Customer Names, and Card Issuers
customers = [str(uuid.uuid4()) for _ in range(num_customers)]
customer_cards = {customer: [str(uuid.uuid4()) for _ in range(random.randint(1, max_cards_per_customer))] for customer in customers}

# Map each customer ID to a unique name
customer_names = {customer: fake.name() for customer in customers}

# Map each card ID to a unique issuer
possible_issuers = ["Bank of America", "Chase", "Wells Fargo", "CitiBank"]
card_issuers = {card: random.choice(possible_issuers) for cards in customer_cards.values() for card in cards}

# Pre-generate a limited number of unique merchants
merchants = {}
for _ in range(max_merchants):
    merchant_id = str(uuid.uuid4())
    merchants[merchant_id] = {
        "merchant_name": fake.company(),
        "merchant_location": {
            "city": fake.city(),
            "state": fake.state_abbr(),
            "country": "UK"  # Default to UK for domestic transactions
        },
        "merchant_terminal_id": "T" + str(random.randint(1000, 9999))
    }

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

        # Randomly select an existing merchant from the pre-generated merchants
        merchant_id = random.choice(list(merchants.keys()))
        merchant_details = merchants[merchant_id]
        
        # Determine account type and corresponding card type
        account_type = random.choice(["debit", "credit", "saving"])
        if account_type == "debit":
            card_type = "Visa"
        elif account_type == "credit":
            card_type = random.choice(["Visa", "MasterCard"])
        elif account_type == "saving":
            card_type = "Visa"
        
        # Determine the payment channel
        payment_channel = random.choice(["POS", "online", "mobile_app"])

        # Set payment method based on payment channel
        if payment_channel == "POS":
            payment_method = random.choice(["swipe", "NFC", "chip"])
        else:
            payment_method = "CNP"

        # Only populate 3D Secure status for online transactions
        if payment_channel == "online":
            three_d_secure_status = random.choice(["Passed", "Failed"])
        else:
            three_d_secure_status = None

        # Populate device ID and IP address for online and mobile app transactions
        if payment_channel in ["online", "mobile_app"]:
            device_id = str(uuid.uuid4())
            ip_address = fake.ipv4()
        else:
            device_id = None
            ip_address = None

        # Populate user agent only for online transactions
        if payment_channel == "online":
            user_agent = fake.user_agent()
        else:
            user_agent = None

        # Determine if the transaction is domestic or international
        is_domestic = random.choices([True, False], weights=[domestic_percentage, 100 - domestic_percentage])[0]
        if is_domestic:
            country = "UK"
            currency = "GBP"
        else:
            country = fake.country_code()
            currency = random.choice(["USD", "EUR", "CAD", "JPY", "AUD"])  # Random foreign currency
        
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "customer_id": customer,
            "card_id": card,
            "transaction_type": payment_channel,
            "transaction_date_time": transaction_date,
            "transaction_amount": generate_transaction_amount(),
            "currency": currency,
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
            "merchant_location": {
                "city": merchant_details["merchant_location"]["city"] if is_domestic else fake.city(),
                "state": merchant_details["merchant_location"]["state"] if is_domestic else fake.state_abbr(),
                "country": country
            },
            "merchant_terminal_id": merchant_details["merchant_terminal_id"],
            "payment_method": payment_method,
            "payment_channel": payment_channel,
            "geolocation": {
                "latitude": fake.latitude(),
                "longitude": fake.longitude()
            },
            "authorization_code": str(random.randint(100000, 999999)),
            "authentication_method": random.choice(["PIN", "biometric", "password"]),
            "3d_secure_status": three_d_secure_status,
            "fraud_risk_score": random.randint(0, 100),
            "transaction_status": random.choice(["approved", "pending", "failed"]),
            "failure_reason": random.choice(["insufficient funds", "fraud detected", "technical error", None]),
            "exchange_rate": round(random.uniform(0.5, 1.5), 2) if not is_domestic else None,
            "rewards_earned": random.randint(0, 10),
            "ip_address": ip_address,
            "device_id": device_id,
            "user_agent": user_agent,
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
