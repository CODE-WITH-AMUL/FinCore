import secrets


def generate_supplier_code():
    prefix = "SUP"
    random_number = secrets.randbelow(90000) + 10000  # 5-digit number [10000, 99999]
    return f"{prefix}{random_number}"


def reference_number_code():
    prefix = "EXP-"
    random_number = secrets.randbelow(90000) + 10000  # 5-digit number [10000, 99999]
    return f"{prefix}{random_number}"