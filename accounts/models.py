from django.db import models
from django.contrib.auth.models import User


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
        verbose_name = "Company Information"
        verbose_name_plural = "Company Information"

    def __str__(self):
        return self.company_name or "Unnamed Company"


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

    company = models.OneToOneField(
        CompanyInformation,
        on_delete=models.SET_NULL,
        related_name="user_profile",
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