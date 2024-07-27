from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from .status import RoleChoices, LanguageChoices, JobStatusChoices, OrderStatusChoices, ProposalStatusChoices, RatingChoices
from datetime import timezone
from django.contrib.postgres.fields import ArrayField


class CustomUserManager(BaseUserManager):
    def create_user(self, user_id, password=None, roles=None, **extra_fields):
        if not user_id:
            raise ValueError('The User_id field must be set')
        
        if roles is None:
            roles = []
            
        user = self.model(user_id=user_id, roles=roles, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('roles', ['Admin']) 
        return self.create_user(user_id, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    roles = ArrayField(
        models.CharField(max_length=20, choices=RoleChoices.choices),
        blank=True,
        default=list,
    )
    phone_number = models.CharField(max_length=14, blank=True, null=True, unique=True)
    language = models.CharField(max_length=20, choices=LanguageChoices.choices, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    tg_username = models.CharField(max_length=30, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = []

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return str(self.user_id)


class Passport(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='passports')
    series = models.CharField(max_length=4, null=True, blank=True)
    number = models.CharField(max_length=6, null=True, blank=True) 
    date_of_issue = models.DateField()  # Дата выдачи паспорта
    issuing_authority = models.CharField(max_length=255) 
    pinfl = models.CharField(max_length=20, null=True, blank=True)

    def clean(self):
        super().clean()
        if not self.series.isalpha() or not self.series.isupper() or len(self.series) != 2:
            raise ValidationError('The series must consist of two uppercase letters.')
        if not self.number.isdigit() or len(self.number) == 7:
            raise ValidationError('The number must consist of seven digits.')

    def save(self, *args, **kwargs):
        self.full_clean()  # Проверка данных перед сохранением
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.series}{self.number}'
    

# only for Role.Worker
class BankCard(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    holder_name = models.CharField(max_length=255)
    card_number = models.BigIntegerField(
        validators=[MinValueValidator(1000000000000000)],
        help_text="Enter a card number with up to 16 digits."
    )
    
    
    def __str__(self):
        return f"Card # {self.holder_name} - {self.card_number}"


# only for Role.Worker
class Cv(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    rating = models.CharField(max_length=1, choices=RatingChoices.choices)

    def __str__(self):
        return f"CV of {self.owner.user_id}"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Order(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    image = models.CharField(max_length=255) 
    location = models.CharField(max_length=255)
    location_link = models.CharField(max_length=255, null=True, blank=True)
    price = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=OrderStatusChoices.choices, default=OrderStatusChoices.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.description}"


# only for Role.Worker
class Proposal(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='proposals', default=None)
    message = models.TextField()
    price = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=ProposalStatusChoices.choices, default=ProposalStatusChoices.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal #{self.id} - {self.owner.user_id} on Order #{self.order.id}"


class Job(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    price = models.CharField(max_length=50)
    status = models.CharField(max_length=15, choices=JobStatusChoices.choices, default=JobStatusChoices.INPROGRESS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assignee = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, related_name='assigned_jobs')
    rating = models.CharField(max_length=1, choices=RatingChoices.choices, null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    job_appeal = models.TextField(null=True, blank=True)
    payment_appeal = models.TextField(null=True, blank=True)
    status_history = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Job for Order {self.order.id} - Status: {self.status}"

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Job.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                self.status_history = f"{timezone.now()}: {self.get_status_display()} -> {self.status}\n" + (self.status_history or "")
        super().save(*args, **kwargs)

