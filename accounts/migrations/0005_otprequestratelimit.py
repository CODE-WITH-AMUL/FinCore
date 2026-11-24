from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_emailotp'),
    ]

    operations = [
        migrations.CreateModel(
            name='OTPRequestRateLimit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=320, unique=True)),
                ('last_issued_at', models.DateTimeField(blank=True, null=True)),
                ('window_started_at', models.DateTimeField()),
                ('request_count', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]