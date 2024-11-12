import pandas as pd
import random
from faker import Faker

# Initialize Faker
fake = Faker()

def generate_numbers(num_type='integer', num_digits=10, unique_count=100, secondary_unique_count=None, secondary_digits=None):
    """
    Generate unique numbers based on the specified type, number of digits, and volume.
    Optionally, generate secondary unique numbers for each primary number.

    Args:
        num_type (str): Type of number ('integer' or 'float').
        num_digits (int): Number of digits for the primary number.
        unique_count (int): Number of unique primary values to generate.
        secondary_unique_count (int, optional): Max unique secondary numbers per primary number.
        secondary_digits (int, optional): Number of digits for each secondary number if needed.

    Returns:
        dict: A dictionary of primary numbers with lists of secondary numbers (if specified),
              or a list of unique primary numbers if no secondary count is given.
    """
    numbers = set()
    lower_bound = 10**(num_digits - 1)
    upper_bound = (10**num_digits) - 1
    
    # Generate primary unique numbers
    while len(numbers) < unique_count:
        if num_type == 'integer':
            num = random.randint(lower_bound, upper_bound)
        elif num_type == 'float':
            num = round(random.uniform(lower_bound, upper_bound), 2)
        else:
            raise ValueError("num_type must be 'integer' or 'float'")
        
        numbers.add(num)

    primary_numbers = list(numbers)
    
    # If secondary numbers are requested, generate them for each primary number
    if secondary_unique_count and secondary_digits:
        secondary_data = {}
        for primary in primary_numbers:
            secondary_data[primary] = [
                generate_secondary_number(num_type, secondary_digits) for _ in range(secondary_unique_count)
            ]
        return secondary_data
    
    return primary_numbers

def generate_secondary_number(num_type, num_digits):
    """Helper function to generate a single number with specified type and digits."""
    lower_bound = 10**(num_digits - 1)
    upper_bound = (10**num_digits) - 1
    
    if num_type == 'integer':
        return random.randint(lower_bound, upper_bound)
    elif num_type == 'float':
        return round(random.uniform(lower_bound, upper_bound), 2)
    else:
        raise ValueError("num_type must be 'integer' or 'float'")

# Generate data: 2 unique party keys, each with a maximum of 5 account keys
party_keys_with_accounts = generate_numbers(
    num_type='integer', num_digits=10, unique_count=2, 
    secondary_unique_count=5, secondary_digits=14
)

# Convert the generated data to a pandas DataFrame and add fake details for each party key
data = []
for party_key, account_keys in party_keys_with_accounts.items():
    # Generate fake details only once per party_key
    party_name = fake.name()
    party_dob = fake.date_of_birth(minimum_age=18, maximum_age=90)
    party_address = fake.address()
    
    for account_key in account_keys:
        data.append({
            'party_key': party_key,
            'account_key': account_key,
            'name': party_name,
            'dob': party_dob,
            'address': party_address
        })

df = pd.DataFrame(data)
print(df)
