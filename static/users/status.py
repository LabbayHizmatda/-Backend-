from django.db import models


class RoleChoices(models.TextChoices):
    ADMIN = 'Admin', 'Админ'
    CUSTOMER = 'Customer', 'Заказчик'
    WORKER = 'Worker', 'Работник'


class LanguageChoices(models.TextChoices):
    RUSSIAN = 'Russian', 'Русский'
    UZBEK = 'Uzbek', 'Uzbek'


class RatingChoices(models.TextChoices):
    ONE = '1', '1'
    TWO = '2', '2'
    THREE = '3', '3'
    FOUR = '4', '4'
    FIVE = '5', '5'


class OrderStatusChoices(models.TextChoices):
    OPEN = "open", "Open"
    Closed = "closed", "Closed"
    JOB = "job", "Job"


class ProposalStatusChoices(models.TextChoices):
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    WAITING = "waiting", "Waiting"
    CANCELED = "canceled", "Canceled"


class JobStatusChoices(models.TextChoices):
    INPROGRESS = "in_progress", "In Progress"
    PAYMENT = "payment", "Payment"
    WARNING = "warning", "Warning"
    REVIEW = "review", "Review"
    COMPLETED = "completed", "Completed"


class AppealTypeChoices(models.TextChoices):
    PAYMENT = 'Payment', 'Оплата'
    JOB = 'Job', 'Работа'


class PaymentStatusChoices(models.TextChoices):
    APPROVED = "Approved", "approved"
    PROBLEM = "Problem", "problem"
    DEFAULT = "Default", "default"