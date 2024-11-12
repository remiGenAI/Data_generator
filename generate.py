import random
import numpy as np

def generate_numbers(num_type='integer', num_digits=10, unique_count=100):
    """
    Generate unique numbers based on the specified type, number of digits, and volume.
    
    Args:
        num_type (str): Type of number ('integer' or 'float').
        num_digits (int): Number of digits for the number.
        unique_count (int): Number of unique values to generate.

    Returns:
        list: List of unique generated numbers.
    """
    numbers = set()
    lower_bound = 10**(num_digits - 1)
    upper_bound = (10**num_digits) - 1
    
    while len(numbers) < unique_count:
        if num_type == 'integer':
            num = random.randint(lower_bound, upper_bound)
        
        elif num_type == 'float':
            num = round(random.uniform(lower_bound, upper_bound), 2)
        
        else:
            raise ValueError("num_type must be 'integer' or 'float'")
        
        numbers.add(num)
    
    return list(numbers)

# Example usage
integer_numbers = generate_numbers(num_type='integer', num_digits=10, unique_count=50)
float_numbers = generate_numbers(num_type='float', num_digits=6, unique_count=30)

print("Generated Integer Numbers:", integer_numbers)
print("Generated Float Numbers:", float_numbers)
