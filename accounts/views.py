import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as user_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.shortcuts import redirect, render

from .management.otp import create_and_send_otp, verify_otp
from .models import UserLoginPrefernce, UserProfileData
from .serializers import SetPasswordSerializer


logger = logging.getLogger(__name__)


def signin(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        user = authenticate(
            request,
            username=email,
            password=request.POST.get("password", ""),
        )
        if user is None:
            messages.error(request, "Invalid email or password.")
        else:
            login(request, user)
            request.session.set_expiry(60 * 60 * 24 * 30)
            return redirect("home")

    return render(request, "authentication/login.html")


def signup(request):
    if request.method != "POST":
        return render(request, "authentication/signup.html")

    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    confirm_password = request.POST.get("confirm_password", "")

    if not all([first_name, last_name, email, password, confirm_password]):
        messages.error(request, "All fields are required.")
        return redirect("signup")
    if password != confirm_password:
        messages.error(request, "Passwords do not match.")
        return redirect("signup")
    if User.objects.filter(email=email).exists():
        messages.error(request, "Email already exists. Please use a different email.")
        return redirect("signup")
    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, "Invalid email format.")
        return redirect("signup")

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=False,
            )
            UserLoginPrefernce.objects.create(user=user, email=email)
            UserProfileData.objects.create(user=user, name=f"{first_name} {last_name}")
            create_and_send_otp(email, request.META.get("REMOTE_ADDR"))
    except Exception:
        logger.exception("Error creating account or sending signup OTP")
        messages.error(request, "Unable to create your account right now.")
        return render(request, "authentication/signup.html")

    request.session["signup_email"] = email
    return redirect("verify_signup_otp")


def verify_signup_otp(request):
    email = request.session.get("signup_email")
    if not email:
        return redirect("signup")

    if request.method == "POST":
        success, message = verify_otp(email, request.POST.get("otp", ""))
        if success:
            User.objects.filter(email=email).update(is_active=True)
            request.session.pop("signup_email", None)
            return redirect("signin")
        messages.error(request, message)

    return render(
        request,
        "authentication/verify_otp.html",
        {"verification_type": "signup", "verification_email": email},
    )


@login_required
def logout(request):
    user_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("signin")


def forget_password(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if User.objects.filter(email=email).exists():
            try:
                create_and_send_otp(email, request.META.get("REMOTE_ADDR"))
            except ValueError as error:
                messages.error(request, str(error))
                return render(request, "authentication/forget_password.html")
            request.session["reset_email"] = email
            return redirect("verify_reset_otp")
        messages.error(request, "No account found with this email.")
    return render(request, "authentication/forget_password.html")


def verify_reset_otp(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("forget_password")
    if request.method == "POST":
        success, message = verify_otp(email, request.POST.get("otp", ""))
        if success:
            request.session["reset_otp_verified"] = True
            return redirect("set_new_password")
        messages.error(request, message)
    return render(request, "authentication/verify_otp.html", {"verification_type": "reset"})


def set_new_password(request):
    email = request.session.get("reset_email")
    if not email or not request.session.get("reset_otp_verified"):
        return redirect("forget_password")
    if request.method == "POST":
        data = request.POST.copy()
        data["email"] = email
        serializer = SetPasswordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            request.session.pop("reset_email", None)
            request.session.pop("reset_otp_verified", None)
            messages.success(request, "Password updated successfully.")
            return redirect("signin")
        for error in serializer.errors.values():
            messages.error(request, " ".join(str(item) for item in error))
    return render(request, "authentication/set_new_password.html", {"email": email})
    
