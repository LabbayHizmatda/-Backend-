# Generated by Django 5.0.7 on 2024-08-11 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_revokedtoken'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RevokedToken',
        ),
    ]