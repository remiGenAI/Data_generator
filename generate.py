import json
import random
from faker import Faker
import numpy as np
import pandas as pd

# Initialize Faker
fake = Faker()

# Load config file
with open("config.json", "r") as f:
    config = json.load(f)

# Helper functions for data generation

def generate_party_key(customer_id):
    """Generate 10-digit customer ID."""
    return f"{customer_id:010}"

def generate_account_key(customer_id, acc_id):
    """Generate 14-digit account ID."""
    return f"{customer_id:010}{acc_id:04}"

def generate_transaction_key(account_key, txn_id):
    """Generate 20-digit transaction ID."""
    return f"{account_key}{txn_id:06}"

def generate_transaction_type():
    """Randomly select a transaction type."""
    return random.choice(config["transaction_types"])

def generate_amount():
    """Generate a transaction amount following gamma distribution."""
    amount = np.random.gamma(config["gamma_distribution"]["alpha"], config["gamma_distribution"]["beta"])
    # Round 10% of amounts
    if random.random() < config["amount_rounding_percentage"]:
        amount = round(amount)
    return round(amount, 2)

def generate_scd_flag(transaction_type):
    """Set CRE or DEB based on transaction type."""
    return "DEB" if transaction_type.endswith("OUT") else "CRE"

def generate_channel():
    """Randomly select a channel."""
    return random.choice(config["channels"])

def generate_demand_indicator():
    """Randomly select a demand indicator."""
    return random.choice(config["demand_indicators"])

def generate_sudexr():
    """Sample sudexr based on weighted probabilities."""
    return random.choices(
        population=list(config["sudexr"].keys()),
        weights=list(config["sudexr"].values())
    )[0]

def generate_execution_date():
    """Generate a random date for the transaction."""
    return fake.date_this_year().strftime("%Y-%m-%d")

def get_rule_id(transaction_type):
    """Return the rule ID based on transaction type."""
    return config["rule_ids"][transaction_type]

def get_look_back_gap(rule_id):
    """Get look-back gap based on rule ID."""
    return config["look_back_gaps"].get(rule_id, "N/A")

# Data generation logic

def generate_data():
    data = []
    for customer_id in range(1, config["unique_customers"] + 1):
        party_key = generate_party_key(customer_id)
        name = fake.name()
        for acc_id in range(1, random.randint(1, config["unique_accounts_per_customer"]) + 1):
            account_key = generate_account_key(customer_id, acc_id)
            for txn_id in range(1, random.randint(1, config["transactions_per_account_per_day"]) + 1):
                transaction_key = generate_transaction_key(account_key, txn_id)
                transaction_type = generate_transaction_type()
                amount = generate_amount()
                scd_flag = generate_scd_flag(transaction_type)
                channel = generate_channel()
                demand_indicator = generate_demand_indicator()
                sudexr_val = generate_sudexr()
                date_time = generate_execution_date()
                business_date = date_time
                rule_id = get_rule_id(transaction_type)
                txn_group = transaction_type
                look_back_gap = get_look_back_gap(rule_id)
                
                # Append transaction data to list
                data.append({
                    "party_key": party_key,
                    "name": name,
                    "account_key": account_key,
                    "transaction_key": transaction_key,
                    "transaction_type": transaction_type,
                    "amount": amount,
                    "scd_flag": scd_flag,
                    "channel": channel,
                    "demand_indicator": demand_indicator,
                    "sudexr": sudexr_val,
                    "execution_local_date_time": date_time,
                    "business_date": business_date,
                    "rule_id": rule_id,
                    "txn_group": txn_group,
                    "look_back_gap": look_back_gap
                })
    return data

# Generate and save data
data = generate_data()
df = pd.DataFrame(data)
df.to_csv("synthetic_transactions.csv", index=False)
print("Synthetic data generated and saved to 'synthetic_transactions.csv'")
