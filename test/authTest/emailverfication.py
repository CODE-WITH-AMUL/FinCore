import os
import sys
import secrets
from pathlib import Path

# FinCore project root: D:\Everything\FinCore
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "FinBinance.settings",
)

import django
django.setup()

from django.conf import settings
from django.core.mail import send_mail

email = input("Enter your email address: ").strip()

if not email or "@" not in email:
    print("Please enter a valid email address.")
    raise SystemExit(1)

# Generate a secure six-digit OTP
otp = f"{secrets.randbelow(1_000_000):06d}"

try:
    sent = send_mail(
        subject="Your FinCore OTP Verification Code",
        message=(
            f"Your FinCore verification code is: {otp}\n\n"
            "This code expires in 5 minutes.\n"
            "Do not share this code with anyone."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    if sent == 1:
        print(f"OTP sent successfully to {email}.")

        entered_otp = input("Enter the OTP received in your email: ").strip()

        if entered_otp == otp:
            print("SUCCESS: Email OTP verified.")
        else:
            print("ERROR: Invalid OTP.")

    else:
        print("Failed to send OTP.")

except Exception as error:
    print(f"Email error: {type(error).__name__}: {error}")

