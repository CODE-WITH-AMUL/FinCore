import random


def generate_supplier_code():
    prefix = "SUP"  # You can change this prefix as needed
    random_number = random.randint(10000, 99999)  # Generate a random 5-digit number
    return f"{prefix}{random_number}"


def reference_number_code():
    prefix = "EXP-" # it will genrate the reference number for the expension model
    random_number = random.randint(10000, 99999)  # Generate a random 5-digit number
    return f"{prefix}{random_number}"