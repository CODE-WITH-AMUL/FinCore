import secrets


def generate_product_code():
    number = secrets.randbelow(90000000) + 10000000
    return f"SK-{number}"


def generate_isp_code():
    number = secrets.randbelow(90000000) + 10000000
    return f"ISP-{number}"