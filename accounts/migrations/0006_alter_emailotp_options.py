from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_otprequestratelimit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailotp',
            options={
                'indexes': [
                    models.Index(fields=['email'], name='accounts_em_email_b3d765_idx'),
                    models.Index(fields=['expiration_time'], name='accounts_em_expirat_e0db67_idx'),
                    models.Index(fields=['is_verified'], name='accounts_em_is_veri_7a5656_idx'),
                ],
                'verbose_name': 'Email OTP',
                'verbose_name_plural': 'Email OTPs',
            },
        ),
    ]