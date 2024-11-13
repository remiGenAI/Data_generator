import pandas as pd
import random
import uuid
from faker import Faker
from datetime import datetime, timedelta
import numpy as np

# Initialize Faker
fake = Faker()

# Set transaction parameters
num_payments = 1000  # Total number of payments to generate
high_transaction_threshold = 10000  # High amount threshold
frequent_transaction_count = 10     # Number of frequent transactions for volume scenarios
international_transaction_ratio = 0.2  # Ratio of international transactions for some customers

# Function to simulate high transaction volume
def generate_high_volume_transactions(customer_id, n, base_time):
    payments = []
    for _ in range(n):
        payments.append({
            "transaction_id": str(uuid.uuid4()),
            "timestamp": base_time + timedelta(minutes=random.randint(0, 1440)),  # Same day
            "amount": round(random.uniform(100, 5000), 2),  # Regular transaction amount
            "currency": "USD",
            "sender_account_id": customer_id,
            "receiver_account_id": str(uuid.uuid4()),
            "sender_country": "US",
            "receiver_country": "US",
            "payment_channel": random.choice(["ACH", "domestic_transfer"]),
            "purpose": "Regular Payment"
        })
    return payments

# Function to simulate high transaction amount
def generate_high_amount_transaction(customer_id):
    return {
        "transaction_id": str(uuid.uuid4()),
        "timestamp": fake.date_time_between(start_date="-1y", end_date="now"),
        "amount": round(random.uniform(high_transaction_threshold, high_transaction_threshold * 2), 2),
        "currency": "USD",
        "sender_account_id": customer_id,
        "receiver_account_id": str(uuid.uuid4()),
        "sender_country": "US",
        "receiver_country": "US",
        "payment_channel": "wire_transfer",
        "purpose": "High-Value Payment"
    }

# Function to simulate frequent international transactions
def generate_international_transactions(customer_id, n):
    payments = []
    for _ in range(n):
        payments.append({
            "transaction_id": str(uuid.uuid4()),
            "timestamp": fake.date_time_between(start_date="-1y", end_date="now"),
            "amount": round(random.uniform(500, 5000), 2),
            "currency": random.choice(["USD", "EUR", "GBP"]),
            "sender_account_id": customer_id,
            "receiver_account_id": str(uuid.uuid4()),
            "sender_country": "US",
            "receiver_country": random.choice(["UK", "DE", "FR"]),
            "payment_channel": "SWIFT",
            "purpose": "International Transfer"
        })
    return payments

# Function to simulate rapid consecutive transactions
def generate_rapid_consecutive_transactions(customer_id, n, base_time):
    payments = []
    for i in range(n):
        payments.append({
            "transaction_id": str(uuid.uuid4()),
            "timestamp": base_time + timedelta(minutes=i),  # Every minute
            "amount": round(random.uniform(100, 2000), 2),
            "currency": "USD",
            "sender_account_id": customer_id,
            "receiver_account_id": str(uuid.uuid4()),
            "sender_country": "US",
            "receiver_country": "US",
            "payment_channel": random.choice(["mobile_app", "ACH"]),
            "purpose": "Consecutive Small Payment"
        })
    return payments

# Function to simulate location mismatch transactions
def generate_location_mismatch_transactions(customer_id):
    payments = []
    base_time = fake.date_time_between(start_date="-1y", end_date="now")
    locations = [("US", fake.latitude(), fake.longitude()), 
                 ("UK", fake.latitude(), fake.longitude())]
    for loc in locations:
        payments.append({
            "transaction_id": str(uuid.uuid4()),
            "timestamp": base_time + timedelta(hours=random.randint(1, 6)),  # Within hours
            "amount": round(random.uniform(100, 2000), 2),
            "currency": "USD",
            "sender_account_id": customer_id,
            "receiver_account_id": str(uuid.uuid4()),
            "sender_country": loc[0],
            "receiver_country": "US",
            "latitude": loc[1],
            "longitude": loc[2],
            "payment_channel": "SWIFT",
            "purpose": "Location Discrepancy Test"
        })
    return payments

# Generate the transactions and match scenarios
def generate_payments_with_scenarios(num_payments):
    payments = []
    for _ in range(num_payments):
        customer_id = str(uuid.uuid4())
        
        # Select scenarios based on random sampling
        scenario = random.choice(["high_volume", "high_amount", "frequent_international", "rapid_consecutive", "location_mismatch"])
        
        if scenario == "high_volume":
            # High transaction volume scenario
            payments.extend(generate_high_volume_transactions(customer_id, frequent_transaction_count, datetime.now()))
        
        elif scenario == "high_amount":
            # High transaction amount scenario
            payments.append(generate_high_amount_transaction(customer_id))
        
        elif scenario == "frequent_international":
            # Frequent international transactions
            payments.extend(generate_international_transactions(customer_id, int(num_payments * international_transaction_ratio)))
        
        elif scenario == "rapid_consecutive":
            # Rapid consecutive transactions
            payments.extend(generate_rapid_consecutive_transactions(customer_id, frequent_transaction_count, datetime.now()))
        
        elif scenario == "location_mismatch":
            # Location mismatch transactions
            payments.extend(generate_location_mismatch_transactions(customer_id))
        
    # Create DataFrame
    df = pd.DataFrame(payments)
    return df

# Generate the payment DataFrame with scenarios
df_payments = generate_payments_with_scenarios(num_payments)
df_payments.head()
