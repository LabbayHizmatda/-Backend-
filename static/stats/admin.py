from django.contrib import admin
from .models import UserStats, OrderStats, ProposalStats

admin.site.register(UserStats)
admin.site.register(OrderStats)
admin.site.register(ProposalStats)
