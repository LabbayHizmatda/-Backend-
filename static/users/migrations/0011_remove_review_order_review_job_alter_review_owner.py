# Generated by Django 5.0.7 on 2024-07-29 19:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_review_order_alter_cv_owner_alter_proposal_order_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='order',
        ),
        migrations.AddField(
            model_name='review',
            name='job',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='users.job'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='review',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]