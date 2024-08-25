from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from users.models import CustomUser, Order, Proposal
from .models import UserStats, OrderStats, ProposalStats

@receiver(post_save, sender=CustomUser)
def update_user_stats(sender, instance, created, **kwargs):
    if created:
        today = timezone.now().date()
        stats, _ = UserStats.objects.get_or_create(date=today)
        stats.registered_users += 1
        stats.save()

@receiver(post_save, sender=Order)
def update_order_stats(sender, instance, created, **kwargs):
    if created:
        today = timezone.now().date()
        stats, _ = OrderStats.objects.get_or_create(date=today)
        stats.created_orders += 1
        stats.save()

@receiver(post_save, sender=Proposal)
def update_proposal_stats(sender, instance, created, **kwargs):
    if created:
        today = timezone.now().date()
        stats, _ = ProposalStats.objects.get_or_create(date=today)
        stats.created_proposals += 1
        stats.save()
