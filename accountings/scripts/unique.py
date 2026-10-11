"""
Unique code generators for FinCore.

All generators use `secrets` (cryptographically secure) instead of `random`
to satisfy Bandit B311 and prevent predictable IDs.

Each generator accepts an optional `exists_fn` (callable) that returns True
if the candidate code is already taken. If provided, the generator retries
until a unique code is produced (max 20 attempts).
"""
import secrets


_MAX_ATTEMPTS = 20


def _random_8_digit():
    """Return a random 8-digit integer in the range [10_000_000, 99_999_999]."""
    return secrets.randbelow(90_000_000) + 10_000_000


def _unique(prefix: str, exists_fn=None) -> str:
    """
    Build a code like '{prefix}-{8-digit-number}' and retry on collision
    if `exists_fn` is provided.
    """
    for _ in range(_MAX_ATTEMPTS):
        code = f"{prefix}-{_random_8_digit()}"
        if exists_fn is None or not exists_fn(code):
            return code
    raise RuntimeError(
        f"Could not generate a unique {prefix} code after {_MAX_ATTEMPTS} attempts."
    )


# ============================================================
# Public generators — pass an exists_fn for collision safety
# ============================================================

def generate_product_code(exists_fn=None):
    """e.g. SK-48291037"""
    return _unique("SK", exists_fn)


def generate_isp_code(exists_fn=None):
    """e.g. ISP-73510284"""
    return _unique("ISP", exists_fn)


def generate_sales_sku(exists_fn=None):
    """e.g. SSKU-12938476"""
    return _unique("SSKU", exists_fn)


def generate_invoice_number(exists_fn=None):
    """e.g. INV-48291037"""
    return _unique("INV", exists_fn)


def purchases_number(exists_fn=None):
    """e.g. PUR-73820194"""
    return _unique("PUR", exists_fn)