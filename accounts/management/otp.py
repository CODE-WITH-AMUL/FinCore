import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from ..models import EmailOTP, OTPRequestRateLimit


OTP_EXPIRATION_MINUTES = 5
OTP_RESEND_SECONDS = 60
OTP_MAX_REQUESTS = 5
OTP_WINDOW_HOURS = 1
OTP_MAX_ATTEMPTS = 5


def _hash_otp(otp, salt):
    return hashlib.sha256(f"{salt}:{otp}".encode("utf-8")).hexdigest()


def _rate_limit_key(email, ip_address):
    return f"{email}:{ip_address or 'unknown'}"


def _check_rate_limit(email, ip_address):
    now = timezone.now()
    key = _rate_limit_key(email, ip_address)
    with transaction.atomic():
        limit, _ = OTPRequestRateLimit.objects.select_for_update().get_or_create(
            key=key,
            defaults={
                "window_started_at": now,
                "request_count": 0,
            },
        )

        if now - limit.window_started_at >= timedelta(hours=OTP_WINDOW_HOURS):
            limit.window_started_at = now
            limit.request_count = 0

        if limit.last_issued_at:
            elapsed = (now - limit.last_issued_at).total_seconds()
            if elapsed < OTP_RESEND_SECONDS:
                raise ValueError("Please wait before requesting another OTP.")

        if limit.request_count >= OTP_MAX_REQUESTS:
            raise ValueError("Too many OTP requests. Please try again later.")

        limit.request_count += 1
        limit.last_issued_at = now
        limit.save(update_fields=["window_started_at", "request_count", "last_issued_at"])


def create_and_send_otp(email, ip_address=None):
    email = email.strip().lower()
    _check_rate_limit(email, ip_address)

    otp = f"{secrets.randbelow(1_000_000):06d}"
    salt = secrets.token_hex(16)
    now = timezone.now()

    EmailOTP.objects.update_or_create(
        email=email,
        defaults={
            "otp": _hash_otp(otp, salt),
            "salt": salt,
            "attempts": 0,
            "expiration_time": now + timedelta(minutes=OTP_EXPIRATION_MINUTES),
            "is_verified": False,
            "reset_token": None,
            "reset_token_expires_at": None,
        },
    )

    return send_mail(
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


def verify_otp(email, otp):
    email = email.strip().lower()
    otp = otp.strip()

    try:
        record = EmailOTP.objects.get(email=email)
    except EmailOTP.DoesNotExist:
        return False, "Invalid or expired OTP."

    if record.is_expired:
        return False, "OTP has expired."

    if record.attempts >= OTP_MAX_ATTEMPTS:
        return False, "Too many invalid attempts. Request a new OTP."

    expected = _hash_otp(otp, record.salt)
    if not hmac.compare_digest(record.otp, expected):
        record.attempts += 1
        record.save(update_fields=["attempts"])
        return False, "Invalid OTP."

    record.is_verified = True
    record.save(update_fields=["is_verified"])
    return True, "OTP verified successfully."
