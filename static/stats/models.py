from django.db import models
from django.utils import timezone

class UserStats(models.Model):
    date = models.DateField(unique=True)
    registered_users = models.IntegerField(default=0)

    def __str__(self):
        return f"User Stats for {self.date} - Registered Users: {self.registered_users}"

class OrderStats(models.Model):
    date = models.DateField(unique=True)
    created_orders = models.IntegerField(default=0)

    def __str__(self):
        return f"Order Stats for {self.date} - Created Orders: {self.created_orders}"

class ProposalStats(models.Model):
    date = models.DateField(unique=True)
    created_proposals = models.IntegerField(default=0)

    def __str__(self):
        return f"Proposal Stats for {self.date} - Created Proposals: {self.created_proposals}"
