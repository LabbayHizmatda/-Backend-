# Generated by Django 5.0.7 on 2024-07-30 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_alter_cv_bio_alter_cv_owner_alter_cv_rating_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cv',
            name='word_experience',
            field=models.IntegerField(default=0),
        ),
    ]
