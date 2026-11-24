from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class UniversalTimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserLoginPrefernce(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="login_preference"
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email or self.user.email


TYPE_OF_COMPANY_CHOICES = [
    ("Private Limited", "Private Limited"),
    ("Public Limited", "Public Limited"),
    ("Partnership", "Partnership"),
    ("Sole Proprietorship", "Sole Proprietorship"),
    ("Limited Liability Company (LLC)", "Limited Liability Company (LLC)"),
    ("Nonprofit Organization", "Nonprofit Organization"),
    ("Cooperative", "Cooperative"),
    ("Joint Venture", "Joint Venture"),
    ("Franchise", "Franchise"),
    ("Government-Owned Corporation", "Government-Owned Corporation"),
    ("Multinational Corporation (MNC)", "Multinational Corporation (MNC)"),
    ("Holding Company", "Holding Company"),
    ("Subsidiary", "Subsidiary"),
    ("Conglomerate", "Conglomerate"),
    ("Professional Corporation (PC)", "Professional Corporation (PC)"),
    ("Benefit Corporation (B Corp)", "Benefit Corporation (B Corp)"),
    ("Public-Private Partnership (PPP)", "Public-Private Partnership (PPP)"),
    ("Limited Liability Partnership (LLP)", "Limited Liability Partnership (LLP)"),
    ("S-Corporation", "S-Corporation"),
    ("C-Corporation", "C-Corporation"),
]


class CompanyInformation(UniversalTimeStampModel):
    company_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    company_logo = models.ImageField(
        upload_to="company_logos/",
        blank=True,
        null=True
    )

    company_address = models.TextField(
        blank=True,
        null=True
    )

    company_email = models.EmailField(
        max_length=255,
        blank=True,
        null=True
    )

    company_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    company_office_type = models.CharField(
        max_length=255,
        choices=TYPE_OF_COMPANY_CHOICES,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.company_name or "Unnamed Organization"

    @property
    def display_name(self):
        return self.company_name or "Unnamed Organization"

    # Nepal localization & organization settings
    pan_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Permanent Account Number (9-digit PAN/VAT in Nepal)"
    )
    vat_registered = models.BooleanField(
        default=False,
        help_text="Whether this business is registered for VAT (13%)"
    )
    currency = models.CharField(
        max_length=10,
        default="NPR",
        help_text="Default reporting currency"
    )
    timezone = models.CharField(
        max_length=50,
        default="Asia/Kathmandu"
    )
    fiscal_year_start_month = models.PositiveSmallIntegerField(
        default=4,
        help_text="Start month of fiscal year (Shrawan is month 4 in BS calendar, mid-July)"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    state_or_province = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    country = models.CharField(
        max_length=100,
        default="Nepal"
    )
    website = models.URLField(
        max_length=255,
        blank=True,
        null=True
    )


# Alias for domain semantics
Organization = CompanyInformation


class OrganizationRole(models.TextChoices):
    OWNER = "owner", "Owner"
    ADMIN = "admin", "Administrator"
    ACCOUNTANT = "accountant", "Accountant"
    MANAGER = "manager", "Manager"
    STAFF = "staff", "Staff"


class OrganizationMembership(UniversalTimeStampModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organization_memberships"
    )
    organization = models.ForeignKey(
        CompanyInformation,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    role = models.CharField(
        max_length=20,
        choices=OrganizationRole.choices,
        default=OrganizationRole.STAFF
    )
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Organization Membership"
        verbose_name_plural = "Organization Memberships"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_organization_membership"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.organization.company_name} ({self.get_role_display()})"


class OrganizationScopedModel(UniversalTimeStampModel):
    organization = models.ForeignKey(
        CompanyInformation,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        null=True,
        blank=True,
        help_text="Organization that owns this record"
    )

    class Meta:
        abstract = True


class UserProfileData(UniversalTimeStampModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile_data"
    )

    name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    company = models.ForeignKey(
        CompanyInformation,
        on_delete=models.SET_NULL,
        related_name="user_profiles",
        blank=True,
        null=True
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name or self.user.username
    
    
    
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class EmailOTP(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    otp = models.CharField(max_length=64)          # SHA256 hex = 64 chars
    salt = models.CharField(max_length=32)          # 16 bytes hex = 32 chars
    attempts = models.PositiveIntegerField(default=0)
    expiration_time = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    reset_token_expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Email OTP"
        verbose_name_plural = "Email OTPs"
        indexes = [
            models.Index(fields=['email'], name='accounts_em_email_b3d765_idx'),
            models.Index(fields=['expiration_time'], name='accounts_em_expirat_e0db67_idx'),
            models.Index(fields=['is_verified'], name='accounts_em_is_veri_7a5656_idx'),
        ]


    @property
    def is_reset_token_valid(self):
        return (
            bool(self.reset_token)
            and bool(self.reset_token_expires_at)
            and timezone.now() < self.reset_token_expires_at
        )

    @property
    def is_expired(self):
        return timezone.now() > self.expiration_time

    def save(self, *args, **kwargs):
        if not self.expiration_time:
            self.expiration_time = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)


class OTPRequestRateLimit(models.Model):
    key = models.CharField(max_length=320, unique=True)
    last_issued_at = models.DateTimeField(null=True, blank=True)
    window_started_at = models.DateTimeField()
    request_count = models.PositiveIntegerField(default=0)

