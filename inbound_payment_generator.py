import pandas as pd
import random
import uuid
from faker import Faker
from datetime import datetime, timedelta
import numpy as np

# Initialize Faker
fake = Faker()

# Set the number of inbound payments to generate
num_payments = 1000

# Function to simulate inbound payments
def generate_inbound_payments(n):
    data = []
    for _ in range(n):
        # Randomly select sender and receiver countries
        sender_country = fake.country_code()
        receiver_country = "UK" if random.random() < 0.9 else fake.country_code()
        
        # Generate exchange rate if payment is international
        exchange_rate = round(random.uniform(0.5, 1.5), 4) if sender_country != receiver_country else None

        payment = {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": fake.date_time_between(start_date="-1y", end_date="now"),
            "amount": round(random.uniform(10, 100000), 2),
            "currency": random.choice(["USD", "EUR", "GBP", "JPY", "CAD"]),
            "exchange_rate": exchange_rate,
            
            # Sender Information
            "sender_account_id": str(uuid.uuid4()),
            "sender_name": fake.name(),
            "sender_country": sender_country,
            "sender_bank": fake.company() + " Bank",
            "sender_bank_swift": fake.swift(),
            "sender_account_type": random.choice(["personal", "business"]),
            
            # Receiver Information
            "receiver_account_id": str(uuid.uuid4()),
            "receiver_name": fake.name(),
            "receiver_country": receiver_country,
            "receiver_bank": "UK Bank" if receiver_country == "UK" else fake.company() + " Bank",
            "receiver_bank_swift": fake.swift(),
            "receiver_account_type": random.choice(["personal", "business"]),
            
            # Payment Details
            "payment_channel": random.choice(["SWIFT", "ACH", "domestic_transfer", "mobile_app"]),
            "payment_method": random.choice(["wire_transfer", "mobile_payment", "credit_transfer"]),
            "purpose": random.choice(["salary", "gift", "investment", "loan repayment", "invoice payment"]),
            "memo": fake.sentence(nb_words=6),
            
            # Compliance and Screening Fields
            "aml_risk_score": random.randint(1, 100),
            "fraud_check_status": random.choice(["Cleared", "Flagged"]),
            "sanctions_check": random.choice(["Cleared", "Flagged"]),
            "pep_check": random.choice(["Cleared", "Flagged"]),
            
            # Additional Metadata
            "device_id": str(uuid.uuid4()) if random.random() < 0.3 else None,
            "ip_address": fake.ipv4() if random.random() < 0.3 else None,
            "user_agent": fake.user_agent() if random.random() < 0.3 else None,
            "session_id": str(uuid.uuid4()) if random.random() < 0.3 else None
        }
        
        data.append(payment)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    return df

# Generate the inbound payments DataFrame
df_inbound_payments = generate_inbound_payments(num_payments)

# Display the first few rows
df_inbound_payments.head()
