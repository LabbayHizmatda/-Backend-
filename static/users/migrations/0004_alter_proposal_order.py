# Generated by Django 5.0.7 on 2024-07-24 10:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_proposal_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='order',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='proposals', to='users.order'),
        ),
    ]
