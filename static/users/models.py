from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from .status import RoleChoices, LanguageChoices, JobStatusChoices, OrderStatusChoices, ProposalStatusChoices, RatingChoices, AppealTypeChoices, PaymentStatusChoices
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.db.models import Avg, Case, When, IntegerField


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
    roles = ArrayField(models.CharField(max_length=20, choices=RoleChoices.choices), blank=True, default=list)
    phone_number = models.CharField(max_length=14, blank=True, null=True, unique=True)
    language = models.CharField(max_length=20, choices=LanguageChoices.choices, blank=True, null=True)
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
    
    @property
    def cv(self):
        return Cv.objects.get(user=self)
    
    def __str__(self):
        return str(self.user_id)

    class Meta:
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['language']),
            models.Index(fields=['tg_username']),
            models.Index(fields=['date_created']),
        ]


class Passport(models.Model):
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='passports')
    series = models.CharField(max_length=4, null=True, blank=True)
    number = models.CharField(max_length=6, null=True, blank=True) 
    date_of_issue = models.DateField() 
    issuing_authority = models.CharField(max_length=255) 
    pinfl = models.CharField(max_length=20, null=True, blank=True)

    def clean(self):
        super().clean()
        if not self.series.isalpha() or not self.series.isupper() or len(self.series) != 2:
            raise ValidationError('The series must consist of two uppercase letters.')
        if not self.number.isdigit() or len(self.number) == 7:
            raise ValidationError('The number must consist of seven digits.')

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.series}{self.number}'

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['series']),
            models.Index(fields=['number']),
        ]


class BankCard(models.Model):
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='bank_card')
    holder_name = models.CharField(max_length=255)
    card_number = models.BigIntegerField(
        validators=[MinValueValidator(1000000000000000)],
        help_text="Enter a card number with up to 16 digits."
    )
    
    def __str__(self):
        return f"Card # {self.holder_name} - {self.card_number}"

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['card_number']),
        ]


class Cv(models.Model):
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='cv_images/', blank=True, null=True) 
    bio = models.TextField()
    rating = models.CharField(max_length=2, choices=RatingChoices.choices, default=RatingChoices.ONE)
    word_experience = models.IntegerField(default=0) 

    @property
    def reviews(self):
        return Review.objects.filter(whom=self)

    def update_rating(self):
        reviews = self.reviews
        if reviews.exists():
            average_rating = reviews.aggregate(
                avg_rating=Avg(
                    Case(
                        When(rating='1', then=1),
                        When(rating='2', then=2),
                        When(rating='3', then=3),
                        When(rating='4', then=4),
                        When(rating='5', then=5),
                        output_field=IntegerField(),
                    )
                )
            )['avg_rating']
            rounded_rating = self.get_closest_rating(average_rating)
            self.rating = rounded_rating
        else:
            self.rating = RatingChoices.ONE
        self.save()

    def get_closest_rating(self, avg_rating):
        choices = [int(choice.value) for choice in RatingChoices]
        closest_rating = min(choices, key=lambda x: abs(x - avg_rating))
        return str(closest_rating)

    def appeals(self):
        return Appeal.objects.filter(whom=self).count()

    def __str__(self):
        return f"{self.owner}'s CV"

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['rating']),
        ]


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


class Order(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    location = models.CharField(max_length=255)
    location_link = models.CharField(max_length=255, null=True, blank=True)
    price = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=OrderStatusChoices.choices, default=OrderStatusChoices.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.description}"

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]


class Image(models.Model):
    order = models.ForeignKey(Order, related_name='images', on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='order_images/')

    def __str__(self):
        return f"Image for Order #{self.order.id} - {self.image_file.name}"

class Video(models.Model):
    order = models.ForeignKey(Order, related_name='videos', on_delete=models.CASCADE)
    video_file = models.FileField(upload_to='order_videos/')

    def __str__(self):
        return f"Video for Order #{self.order.id} - {self.video_file.name}"
    

class Proposal(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='proposals', default='')
    message = models.TextField()
    price = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=ProposalStatusChoices.choices, default=ProposalStatusChoices.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal #{self.id} - {self.owner.user_id} on Order #{self.order.id}"

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['order']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]


class Job(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    price = models.CharField(max_length=50)
    status = models.CharField(max_length=15, choices=JobStatusChoices.choices, default=JobStatusChoices.INPROGRESS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assignee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='assigned_jobs')
    status_history = models.TextField(null=True, blank=True)


    payment_confirmed_by_customer = models.CharField(max_length=15, choices=PaymentStatusChoices.choices, default=PaymentStatusChoices.DEFAULT)
    payment_confirmed_by_worker = models.CharField(max_length=15, choices=PaymentStatusChoices.choices, default=PaymentStatusChoices.DEFAULT)

    review_written_by_customer = models.BooleanField(default=False)
    review_written_by_worker = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Job for Order {self.order.id} - Status: {self.status}"

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Job.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                # Ensure timezone is imported from django.utils
                self.status_history = f"{timezone.now()}: {self.get_status_display()} -> {self.status}\n" + (self.status_history or "")
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['proposal']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['assignee']),
        ]

class Review(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='reviews')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    whom = models.ForeignKey(Cv, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(choice, choice) for choice in RatingChoices.values])
    comment = models.TextField(null=True)

    def __str__(self):
        return f"Review by {self.owner} for {self.whom} - Rating: {self.rating}"

    class Meta:
        indexes = [
            models.Index(fields=['job']),
            models.Index(fields=['owner']),
            models.Index(fields=['whom']),
            models.Index(fields=['rating']),
        ]


class Appeal(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="appeals")
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    whom = models.ForeignKey(Cv, on_delete=models.CASCADE, related_name='appeals')
    problem = models.TextField(null=True)
    to = models.CharField(max_length=20, choices=AppealTypeChoices.choices)

    def __str__(self):
        return f"Appeal for Job {self.job_id.id} - To: {self.to}"

    class Meta:
        indexes = [
            models.Index(fields=['job']),
            models.Index(fields=['owner']),
            models.Index(fields=['whom']),
            models.Index(fields=['to']),
        ]
