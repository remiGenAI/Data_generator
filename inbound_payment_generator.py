import pandas as pd
import random
import uuid
from faker import Faker
from datetime import datetime, timedelta
import numpy as np

# Initialize Faker
fake = Faker()

# Parameters for transactions
num_payments = 1000  # Total number of transactions (inbound + outbound)
high_transaction_threshold = 10000  # Threshold for high transaction amount
frequent_transaction_count = 10  # Number of transactions for high volume scenario
international_transaction_ratio = 0.2  # Ratio of international transactions

# Function to generate outbound transactions
def generate_outbound_transactions(n):
    transactions = []
    for _ in range(n):
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": fake.date_time_between(start_date="-1y", end_date="now"),
            "amount": round(random.uniform(10, 100000), 2),
            "currency": random.choice(["USD", "EUR", "GBP", "JPY", "CAD"]),
            "transaction_type": "outbound",
            "sender_account_id": str(uuid.uuid4()),
            "receiver_account_id": str(uuid.uuid4()),
            "sender_name": fake.name(),
            "sender_country": fake.country_code(),
            "receiver_country": fake.country_code(),
            "payment_channel": random.choice(["SWIFT", "ACH", "domestic_transfer", "mobile_app"]),
            "payment_method": random.choice(["wire_transfer", "mobile_payment", "credit_transfer"]),
            "purpose": random.choice(["salary", "gift", "investment", "loan repayment", "invoice payment"]),
            "memo": fake.sentence(nb_words=6),
            "aml_risk_score": random.randint(1, 100),
            "fraud_check_status": random.choice(["Cleared", "Flagged"]),
            "sanctions_check": random.choice(["Cleared", "Flagged"]),
            "pep_check": random.choice(["Cleared", "Flagged"]),
            "device_id": str(uuid.uuid4()) if random.random() < 0.3 else None,
            "ip_address": fake.ipv4() if random.random() < 0.3 else None,
            "user_agent": fake.user_agent() if random.random() < 0.3 else None,
            "session_id": str(uuid.uuid4()) if random.random() < 0.3 else None
        }
        transactions.append(transaction)
    return transactions

# Function to generate inbound payments
def generate_inbound_payments(n):
    payments = []
    for _ in range(n):
        payment = {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": fake.date_time_between(start_date="-1y", end_date="now"),
            "amount": round(random.uniform(10, 100000), 2),
            "currency": random.choice(["USD", "EUR", "GBP", "JPY", "CAD"]),
            "transaction_type": "inbound",
            "sender_account_id": str(uuid.uuid4()),
            "receiver_account_id": str(uuid.uuid4()),
            "sender_name": fake.name(),
            "sender_country": fake.country_code(),
            "receiver_country": "US",
            "receiver_bank": "US Bank",
            "payment_channel": random.choice(["SWIFT", "ACH", "domestic_transfer", "mobile_app"]),
            "payment_method": random.choice(["wire_transfer", "mobile_payment", "credit_transfer"]),
            "purpose": random.choice(["salary", "gift", "investment", "loan repayment", "invoice payment"]),
            "memo": fake.sentence(nb_words=6),
            "aml_risk_score": random.randint(1, 100),
            "fraud_check_status": random.choice(["Cleared", "Flagged"]),
            "sanctions_check": random.choice(["Cleared", "Flagged"]),
            "pep_check": random.choice(["Cleared", "Flagged"]),
            "device_id": str(uuid.uuid4()) if random.random() < 0.3 else None,
            "ip_address": fake.ipv4() if random.random() < 0.3 else None,
            "user_agent": fake.user_agent() if random.random() < 0.3 else None,
            "session_id": str(uuid.uuid4()) if random.random() < 0.3 else None
        }
        payments.append(payment)
    return payments

# Function to generate transactions with scenarios for both inbound and outbound transactions
def generate_transactions_with_scenarios(num_payments):
    transactions = []
    for _ in range(num_payments):
        # Randomly determine if the transaction is inbound or outbound
        transaction_type = random.choice(["inbound", "outbound"])
        
        # Scenario-based transaction generation
        if transaction_type == "inbound":
            scenario = random.choice(["high_volume", "high_amount", "frequent_international"])
            if scenario == "high_volume":
                transactions.extend(generate_high_volume_transactions(str(uuid.uuid4()), frequent_transaction_count, datetime.now(), "inbound"))
            elif scenario == "high_amount":
                transactions.append(generate_high_amount_transaction(str(uuid.uuid4()), "inbound"))
            elif scenario == "frequent_international":
                transactions.extend(generate_international_transactions(str(uuid.uuid4()), int(num_payments * international_transaction_ratio), "inbound"))
        else:
            scenario = random.choice(["high_volume", "high_amount", "frequent_international", "rapid_consecutive", "location_mismatch"])
            if scenario == "high_volume":
                transactions.extend(generate_high_volume_transactions(str(uuid.uuid4()), frequent_transaction_count, datetime.now(), "outbound"))
            elif scenario == "high_amount":
                transactions.append(generate_high_amount_transaction(str(uuid.uuid4()), "outbound"))
            elif scenario == "frequent_international":
                transactions.extend(generate_international_transactions(str(uuid.uuid4()), int(num_payments * international_transaction_ratio), "outbound"))
            elif scenario == "rapid_consecutive":
                transactions.extend(generate_rapid_consecutive_transactions(str(uuid.uuid4()), frequent_transaction_count, datetime.now(), "outbound"))
            elif scenario == "location_mismatch":
                transactions.extend(generate_location_mismatch_transactions(str(uuid.uuid4()), "outbound"))
        
    return pd.DataFrame(transactions)

# Generate the transactions DataFrame with scenarios for both inbound and outbound transactions
df_transactions = generate_transactions_with_scenarios(num_payments)
df_transactions.head()
