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
                alerts.append({
                    "alert_id": f"A1-{i}",
                    "customer_id": customer_id,
                    "card_id": card_id,
                    "alert_type": "High Transaction Volume",
                    "crime_type": config['high_transaction_volume']['crime_type'],
                    "details": f"{len(daily_transactions)} transactions in a single day"
                })
        
        # Scenario 2: High Transaction Amount
        if config['high_transaction_amount']['enabled'] and transaction_amount > config['high_transaction_amount']['amount_threshold']:
            alerts.append({
                "alert_id": f"A2-{i}",
                "customer_id": customer_id,
                "card_id": card_id,
                "alert_type": "High Transaction Amount",
                "crime_type": config['high_transaction_amount']['crime_type'],
                "details": f"Transaction amount of {transaction_amount} {currency} exceeds threshold"
            })
        
        # Scenario 3: Unusual Transaction Patterns
        if config['unusual_transaction_patterns']['enabled']:
            recent_transactions = customer_transactions[(customer_transactions['transaction_date_time'] >= transaction_time - timedelta(days=config['unusual_transaction_patterns']['days_threshold']))]
            international_transactions = recent_transactions[recent_transactions['merchant_country'] != 'UK']
            if len(international_transactions) > config['unusual_transaction_patterns']['international_transaction_threshold']:
                alerts.append({
                    "alert_id": f"A3-{i}",
                    "customer_id": customer_id,
                    "alert_type": "Unusual Transaction Patterns",
                    "crime_type": config['unusual_transaction_patterns']['crime_type'],
                    "details": f"{len(international_transactions)} international transactions within {config['unusual_transaction_patterns']['days_threshold']} days"
                })
        
        # Scenario 4: Frequent International Transactions
        if config['frequent_international_transactions']['enabled']:
            domestic_count = len(customer_transactions[customer_transactions['merchant_country'] == 'UK'])
            international_count = len(customer_transactions) - domestic_count
            if domestic_count > 0 and international_count / domestic_count > config['frequent_international_transactions']['international_to_domestic_ratio']:
                alerts.append({
                    "alert_id": f"A4-{i}",
                    "customer_id": customer_id,
                    "alert_type": "Frequent International Transactions",
                    "crime_type": config['frequent_international_transactions']['crime_type'],
                    "details": f"International to domestic transaction ratio is {international_count/domestic_count:.2f}"
                })
        
        # Scenario 5: Rapid Consecutive Transactions
        if config['rapid_consecutive_transactions']['enabled']:
            close_transactions = customer_transactions[(customer_transactions['transaction_date_time'] >= transaction_time - timedelta(minutes=config['rapid_consecutive_transactions']['time_interval_minutes'])) &
                                                       (customer_transactions['transaction_date_time'] <= transaction_time + timedelta(minutes=config['rapid_consecutive_transactions']['time_interval_minutes']))]
            if len(close_transactions) > config['rapid_consecutive_transactions']['transaction_count_threshold']:
                alerts.append({
                    "alert_id": f"A5-{i}",
                    "customer_id": customer_id,
                    "card_id": card_id,
                    "alert_type": "Rapid Consecutive Transactions",
                    "crime_type": config['rapid_consecutive_transactions']['crime_type'],
                    "details": f"{len(close_transactions)} transactions within {config['rapid_consecutive_transactions']['time_interval_minutes']} minutes"
                })
        
        # Scenario 6: Location Mismatch
        if config['location_mismatch']['enabled']:
            recent_transactions = customer_transactions[(customer_transactions['transaction_date_time'] >= transaction_time - timedelta(hours=config['location_mismatch']['time_interval_hours']))]
            for _, recent_txn in recent_transactions.iterrows():
                recent_location = (recent_txn['latitude'], recent_txn['longitude'])
                distance_km = haversine(location[0], location[1], recent_location[0], recent_location[1])
                if distance_km > config['location_mismatch']['distance_threshold_km']:
                    alerts.append({
                        "alert_id": f"A6-{i}",
                        "customer_id": customer_id,
                        "card_id": card_id,
                        "alert_type": "Location Mismatch",
                        "crime_type": config['location_mismatch']['crime_type'],
                        "details": f"Transaction locations {location} and {recent_location} are more than {config['location_mismatch']['distance_threshold_km']} km apart within {config['location_mismatch']['time_interval_hours']} hours"
                    })
                    break  # Avoid multiple alerts for the same transaction
    
    # Create a DataFrame for alerts
    df_alerts = pd.DataFrame(alerts)
    return df_alerts

# Generate the alerts DataFrame
df_alerts = generate_alerts(df_transactions, alert_config)
df_alerts.head()
