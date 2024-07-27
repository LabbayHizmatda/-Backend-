from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Proposal, Job, ProposalStatusChoices, JobStatusChoices, RatingChoices

@receiver(post_save, sender=Proposal)
def create_job_on_proposal_approval(sender, instance, **kwargs):
    if instance.status == ProposalStatusChoices.APPROVED:
        Job.objects.create(
            order=instance.order,
            proposal=instance,
            price=instance.price,
            status=JobStatusChoices.INPROGRESS,
            assignee=instance.owner,
            rating=RatingChoices.THREE,
            review=None,
            job_appeal=None,
            payment_appeal=None,
            status_history=None,
        )

        