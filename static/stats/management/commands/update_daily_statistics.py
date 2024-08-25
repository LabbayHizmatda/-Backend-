# your_app/management/commands/update_daily_statistics.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from stats.models import UserStats, OrderStats, ProposalStats
from users.models import CustomUser, Order, Proposal
class Command(BaseCommand):
    help = "Update daily statistics"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        # Collect statistics for users registered
        registered_users = CustomUser.objects.filter(date_created__date=today).count()
        UserStats.objects.update_or_create(date=today, defaults={'registered_users': registered_users})

        # Collect statistics for orders created
        created_orders = Order.objects.filter(created_at__date=today).count()
        OrderStats.objects.update_or_create(date=today, defaults={'created_orders': created_orders})

        # Collect statistics for proposals created
        created_proposals = Proposal.objects.filter(created_at__date=today).count()
        ProposalStats.objects.update_or_create(date=today, defaults={'created_proposals': created_proposals})

        self.stdout.write(self.style.SUCCESS('Successfully updated daily statistics.'))
