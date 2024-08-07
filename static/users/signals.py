from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Proposal, Job, Appeal
from .status import  ProposalStatusChoices, JobStatusChoices, PaymentStatusChoices
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model


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
def update_status_on_payment_confirmed(sender, instance, **kwargs):
    # Если оба подтвердили оплату
    if instance.payment_confirmed_by_customer == PaymentStatusChoices.APPROVED and instance.payment_confirmed_by_worker == PaymentStatusChoices.APPROVED:
        if instance.status == JobStatusChoices.PAYMENT:
            instance.status = JobStatusChoices.REVIEW
    else:
        # Если хотя бы один из пользователей сообщил о проблеме с оплатой, изменяем статус на WARNING
        if instance.payment_confirmed_by_customer == PaymentStatusChoices.PROBLEM or instance.payment_confirmed_by_worker == PaymentStatusChoices.PROBLEM:
            if instance.status == JobStatusChoices.PAYMENT:
                instance.status = JobStatusChoices.WARNING

    if instance.status != instance.__class__.objects.get(pk=instance.pk).status:
        instance.save(update_fields=['status'])