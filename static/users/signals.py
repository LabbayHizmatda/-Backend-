from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Proposal, Job
from .status import  ProposalStatusChoices, JobStatusChoices, PaymentStatusChoices


User = get_user_model()


@receiver(post_save, sender=Proposal)
def create_job_on_proposal_approval(sender, instance, **kwargs):
    if instance.status == ProposalStatusChoices.APPROVED:
        Job.objects.create(
            order=instance.order,
            proposal=instance,
            price=instance.price,
            status=JobStatusChoices.INPROGRESS,
            assignee=instance.owner,
            status_history=None,
        )


@receiver(post_save, sender=Job)
def update_status_based_on_payment(sender, instance, **kwargs):
    if instance.payment_confirmed_by_customer == PaymentStatusChoices.APPROVED and instance.payment_confirmed_by_worker == PaymentStatusChoices.APPROVED:
        if instance.status == JobStatusChoices.PAYMENT:
            instance.status = JobStatusChoices.REVIEW
        if instance.status == JobStatusChoices.WARNING:
            instance.status = JobStatusChoices.REVIEW  

    elif instance.payment_confirmed_by_customer == PaymentStatusChoices.PROBLEM or instance.payment_confirmed_by_worker == PaymentStatusChoices.PROBLEM:
        if instance.status == JobStatusChoices.PAYMENT:
            instance.status = JobStatusChoices.WARNING
        
    if instance.pk and instance.status != Job.objects.get(pk=instance.pk).status:
        instance.save(update_fields=['status', 'status_history'])


@receiver(post_save, sender=Job)
def update_job_status_to_completed(sender, instance, **kwargs):
    if instance.review_written_by_customer and instance.review_written_by_worker:
        instance.status = JobStatusChoices.COMPLETED
        instance.save(update_fields=['status', 'status_history'])