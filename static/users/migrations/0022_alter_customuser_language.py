# Generated by Django 5.0.7 on 2024-08-07 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_job_payment_confirmed_by_customer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='language',
            field=models.CharField(blank=True, choices=[('Russian', 'Русский'), ('Uzbek', 'Uzbek')], max_length=20, null=True),
        ),
    ]
