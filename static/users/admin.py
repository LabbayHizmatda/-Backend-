from django.contrib import admin
from .models import CustomUser, Passport, BankCard, Cv, Category, Order, Proposal, Job, Review, Appeal, Image, Video
from django import forms
from .status import RoleChoices


class CustomUserForm(forms.ModelForm):
    roles = forms.MultipleChoiceField(
        choices=RoleChoices.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = '__all__'

    def clean_roles(self):
        return self.cleaned_data.get('roles', [])

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserForm
    list_display = ('user_id', 'first_name', 'last_name', 'full_name', 'is_staff', 'is_active', 'roles', 'language')
    list_filter = ('is_staff', 'is_active', 'roles', 'language')
    search_fields = ('user_id',)
    readonly_fields = ('date_created',)

    def save_model(self, request, obj, form, change):
        obj.roles = form.cleaned_data.get('roles', [])
        super().save_model(request, obj, form, change)

@admin.register(Passport)
class PassportAdmin(admin.ModelAdmin):
    list_display = ('owner', 'series', 'number', 'date_of_issue', 'issuing_authority')
    search_fields = ('owner__user_id', 'series', 'number')


@admin.register(BankCard)
class BankCardAdmin(admin.ModelAdmin):
    list_display = ('owner', 'holder_name', 'card_number')
    search_fields = ('owner__user_id', 'holder_name')


@admin.register(Cv)
class CvAdmin(admin.ModelAdmin):
    list_display = ('owner', 'rating')
    search_fields = ('owner__user_id',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1

class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    inlines = [ImageInline, VideoInline]
    list_display = ('id', 'owner', 'category', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'owner__user_id', 'description')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if not change:
            for image in form.cleaned_data.get('images', []):
                image.order = form.instance
                image.save()
            for video in form.cleaned_data.get('videos', []):
                video.order = form.instance
                video.save()


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'order', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'owner__user_id', 'order__id')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'proposal', 'status', 'created_at', 'assignee')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'order__id', 'proposal__id')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('job', 'owner', 'whom', 'rating', 'comment')
    search_fields = ('job__id', 'owner__user_id', 'whom__owner__user_id', 'rating')
    list_filter = ('rating', 'job')

@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ('job', 'owner', 'whom', 'problem', 'to')
    search_fields = ('job__id', 'owner__user_id', 'whom__owner__user_id', 'problem', 'to')
    list_filter = ('to',)


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'image_file')
    search_fields = ('order',)

class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'video_file')
    search_fields = ('order',)

admin.site.register(Image, ImageAdmin)
admin.site.register(Video, VideoAdmin)