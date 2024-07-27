from django.contrib import admin
from .models import CustomUser, Passport, BankCard, Cv, Category, Order, Proposal, Job
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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'category', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'owner__user_id', 'description')


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