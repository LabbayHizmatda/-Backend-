# Generated by Django 5.0.7 on 2024-07-29 20:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_alter_appeal_job_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankcard',
            name='owner',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bank_card', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cv',
            name='owner',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cv', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='passport',
            name='owner',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='passports', to=settings.AUTH_USER_MODEL),
        ),
    ]
