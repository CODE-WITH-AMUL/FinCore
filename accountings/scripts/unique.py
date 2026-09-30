import secrets


def generate_product_code():
    number = secrets.randbelow(90000000) + 10000000
    return f"SK-{number}"


def generate_isp_code():
    number = secrets.randbelow(90000000) + 10000000
    return f"ISP-{number}"

def generate_sales_sku():
    number = secrets.randbelow(90000000) + 10000000
    return f"SSKU-{number}"

def generate_invoice_number():
    number = secrets.randbelow(90000000) + 10000000
    return f"INV-{number}"