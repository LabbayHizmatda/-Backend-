from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Proposal, Job
from .status import  ProposalStatusChoices, JobStatusChoices
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