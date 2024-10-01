from celery import shared_task
from django.core.management import call_command

@shared_task
def update_daily_statistics():
    call_command('update_daily_statistics')