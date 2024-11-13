import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from datetime import timedelta
import json

# Load TM alert scenarios from config file
with open("alert_scenarios.json", "r") as f:
    alert_config = json.load(f)

# Load transaction data from synthetic_transactions.csv
df_transactions = pd.read_csv("synthetic_transactions.csv")

# Convert transaction date-time to pandas datetime for easy manipulation
df_transactions['transaction_date_time'] = pd.to_datetime(df_transactions['transaction_date_time'])

# Haversine function to calculate distance in kilometers between two latitude/longitude points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Narrative templates
narrative_templates = {
    "High Transaction Volume": "Customer {customer_id} conducted {transaction_count} transactions on {date}, which exceeds the typical volume threshold. This activity could indicate structuring to avoid detection.",
    "High Transaction Amount": "A single transaction of {transaction_amount} {currency} was flagged for Customer {customer_id} on {date}. This amount exceeds the high-value threshold and warrants further investigation.",
    "Frequent International Transactions": "Customer {customer_id} conducted {international_count} international transactions to {receiver_country} within a short period. This frequent cross-border activity may indicate potential involvement in money laundering or evasion of currency controls.",
    "Rapid Consecutive Transactions": "Customer {customer_id} initiated {transaction_count} transactions within {time_interval} minutes on {date}. Rapid consecutive transactions may suggest structuring or smurfing activity.",
    "Location Mismatch": "Customer {customer_id} conducted transactions from different locations ({location_1} and {location_2}) within {time_interval} hours. This discrepancy may indicate possible account compromise or unauthorized access."
}

# Function to generate a narrative based on alert type and details
def generate_narrative(alert_type, details):
    template = narrative_templates.get(alert_type, "No narrative available for this alert type.")
    return template.format(**details)

# Function to generate alerts based on scenarios
def generate_alerts(transactions, config):
    alerts = []
    
    for i, transaction in transactions.iterrows():
        customer_id = transaction['customer_id']
        card_id = transaction['card_id']
        transaction_time = transaction['transaction_date_time']
        transaction_amount = transaction['transaction_amount']
        payment_channel = transaction['payment_channel']
        currency = transaction['currency']
        location = (transaction['latitude'], transaction['longitude'])
        
        # Skip transactions with missing geolocation data
        if pd.isna(location[0]) or pd.isna(location[1]):
            continue

        # Filter transactions for the same customer and card
        customer_transactions = transactions[transactions['customer_id'] == customer_id]
        card_transactions = transactions[transactions['card_id'] == card_id]
        
        # Scenario 1: High Transaction Volume
        if config['high_transaction_volume']['enabled']:
            daily_transactions = card_transactions[card_transactions['transaction_date_time'].dt.date == transaction_time.date()]
            if len(daily_transactions) > config['high_transaction_volume']['transactions_per_day_threshold']:
                details = {
                    "customer_id": customer_id,
                    "transaction_count": len(daily_transactions),
                    "date": transaction_time.date()
                }
                alerts.append({
                    "alert_id": f"A1-{i}",
                    "customer_id": customer_id,
                    "card_id": card_id,
                    "alert_type": "High Transaction Volume",
                    "crime_type": config['high_transaction_volume']['crime_type'],
                    "details": f"{len(daily_transactions)} transactions in a single day",
                    "narrative": generate_narrative("High Transaction Volume", details)
                })
        
        # Scenario 2: High Transaction Amount
        if config['high_transaction_amount']['enabled'] and transaction_amount > config['high_transaction_amount']['amount_threshold']:
            details = {
                "customer_id": customer_id,
                "transaction_amount": transaction_amount,
                "currency": currency,
                "date": transaction_time.date()
            }
            alerts.append({
                "alert_id": f"A2-{i}",
                "customer_id": customer_id,
                "card_id": card_id,
                "alert_type": "High Transaction Amount",
                "crime_type": config['high_transaction_amount']['crime_type'],
                "details": f"Transaction amount of {transaction_amount} {currency} exceeds threshold",
                "narrative": generate_narrative("High Transaction Amount", details)
            })
        
        # Scenario 3: Frequent International Transactions
        if config['frequent_international_transactions']['enabled']:
            domestic_count = len(customer_transactions[customer_transactions['merchant_country'] == 'UK'])
            international_count = len(customer_transactions) - domestic_count
            if domestic_count > 0 and international_count / domestic_count > config['frequent_international_transactions']['international_to_domestic_ratio']:
                details = {
                    "customer_id": customer_id,
                    "international_count": international_count,
                    "receiver_country": transaction['merchant_country']
                }
                alerts.append({
                    "alert_id": f"A4-{i}",
                    "customer_id": customer_id,
                    "alert_type": "Frequent International Transactions",
                    "crime_type": config['frequent_international_transactions']['crime_type'],
                    "details": f"International to domestic transaction ratio is {international_count/domestic_count:.2f}",
                    "narrative": generate_narrative("Frequent International Transactions", details)
                })
        
        # Scenario 4: Rapid Consecutive Transactions
        if config['rapid_consecutive_transactions']['enabled']:
            close_transactions = customer_transactions[(customer_transactions['transaction_date_time'] >= transaction_time - timedelta(minutes=config['rapid_consecutive_transactions']['time_interval_minutes'])) &
                                                       (customer_transactions['transaction_date_time'] <= transaction_time + timedelta(minutes=config['rapid_consecutive_transactions']['time_interval_minutes']))]
            if len(close_transactions) > config['rapid_consecutive_transactions']['transaction_count_threshold']:
                details = {
                    "customer_id": customer_id,
                    "transaction_count": len(close_transactions),
                    "time_interval": config['rapid_consecutive_transactions']['time_interval_minutes'],
                    "date": transaction_time.date()
                }
                alerts.append({
                    "alert_id": f"A5-{i}",
                    "customer_id": customer_id,
                    "card_id": card_id,
                    "alert_type": "Rapid Consecutive Transactions",
                    "crime_type": config['rapid_consecutive_transactions']['crime_type'],
                    "details": f"{len(close_transactions)} transactions within {config['rapid_consecutive_transactions']['time_interval_minutes']} minutes",
                    "narrative": generate_narrative("Rapid Consecutive Transactions", details)
                })
        
        # Scenario 6: Location Mismatch
        if config['location_mismatch']['enabled']:
            recent_transactions = customer_transactions[(customer_transactions['transaction_date_time'] >= transaction_time - timedelta(hours=config['location_mismatch']['time_interval_hours']))]
            for _, recent_txn in recent_transactions.iterrows():
                recent_location = (recent_txn['latitude'], recent_txn['longitude'])
                distance_km = haversine(location[0], location[1], recent_location[0], recent_location[1])
                if distance_km > config['location_mismatch']['distance_threshold_km']:
                    details = {
                        "customer_id": customer_id,
                        "location_1": f"{location[0]}, {location[1]}",
                        "location_2": f"{recent_location[0]}, {recent_location[1]}",
                        "time_interval": config['location_mismatch']['time_interval_hours']
                    }
                    alerts.append({
                        "alert_id": f"A6-{i}",
                        "customer_id": customer_id,
                        "card_id": card_id,
                        "alert_type": "Location Mismatch",
                        "crime_type": config['location_mismatch']['crime_type'],
                        "details": f"Transaction locations {location} and {recent_location} are more than {config['location_mismatch']['distance_threshold_km']} km apart within {config['location_mismatch']['time_interval_hours']} hours",
                        "narrative": generate_narrative("Location Mismatch", details)
                    })
                    break  # Avoid multiple alerts for the same transaction
    
    # Create a DataFrame for alerts
    df_alerts = pd.DataFrame(alerts)
    return df_alerts

# Generate the alerts DataFrame
df_alerts = generate_alerts(df_transactions, alert_config)
df_alerts.head()
