import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import EmailOTP
from .management.otp import create_and_send_otp, verify_otp


User = get_user_model()


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.strip().lower()
        return value

    def create(self, validated_data):
        email = validated_data['email']
        if User.objects.filter(email=email).exists():
            create_and_send_otp(email)
        return validated_data


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        attrs['email'] = attrs['email'].strip().lower()
        attrs['otp'] = attrs['otp'].strip()

        success, message = verify_otp(attrs['email'], attrs['otp'])
        if not success:
            raise serializers.ValidationError({"otp": message})

        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        token = secrets.token_urlsafe(32)

        EmailOTP.objects.filter(email=email).update(
            reset_token=token,
            reset_token_expires_at=timezone.now() + timedelta(minutes=10),
        )

        return {"email": email, "reset_token": token}

class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        attrs['email'] = attrs['email'].strip().lower()

        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        try:
            record = EmailOTP.objects.get(
                email=attrs['email'],
                reset_token=attrs['reset_token'],
            )
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError(
                {"reset_token": "Invalid reset token."}
            )

        if not record.is_reset_token_valid:
            raise serializers.ValidationError(
                {"reset_token": "Reset token has expired."}
            )

        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "No account found with this email."}
            )

        try:
            validate_password(attrs['new_password'], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )

        attrs['user'] = user
        attrs['record'] = record
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        email = validated_data['email']
        reset_token = validated_data['reset_token']

        with transaction.atomic():
            try:
                record = EmailOTP.objects.select_for_update().get(
                    email=email,
                    reset_token=reset_token,
                )
            except EmailOTP.DoesNotExist:
                raise serializers.ValidationError(
                    {"reset_token": "Invalid reset token."}
                )
            if not record.is_reset_token_valid:
                raise serializers.ValidationError(
                    {"reset_token": "Reset token has expired."}
                )

            user.set_password(validated_data['new_password'])
            user.save(update_fields=['password'])

            record.reset_token = None
            record.reset_token_expires_at = None
            record.is_verified = False
            record.save(update_fields=[
                'reset_token', 'reset_token_expires_at', 'is_verified',
            ])
        return user