import django_filters
from django_filters import rest_framework as filters
from .models import CustomUser, Passport, Order, Proposal, Job, Review, Appeal
from django.db.models import IntegerField, Q
from django.db.models.functions import Cast

class PriceRangeFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(method='filter_by_min_price')
    max_price = django_filters.NumberFilter(method='filter_by_max_price')

    class Meta:
        fields = ['min_price', 'max_price']

    def filter_by_min_price(self, queryset, name, value):
        return queryset.annotate(
            numeric_price=Cast('price', IntegerField())
        ).filter(numeric_price__gte=value)

    def filter_by_max_price(self, queryset, name, value):
        return queryset.annotate(
            numeric_price=Cast('price', IntegerField())
        ).filter(numeric_price__lte=value)
        


class CustomUserFilter(filters.FilterSet):
    user_id = filters.NumberFilter()
    full_name = filters.CharFilter(field_name='full_name', lookup_expr='icontains')
    roles = filters.CharFilter(field_name='roles', lookup_expr='icontains')
    phone_number = filters.CharFilter(lookup_expr='icontains')
    language = filters.CharFilter(lookup_expr='icontains')
    tg_username = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = CustomUser
        fields = ['user_id', 'full_name', 'roles', 'phone_number', 'language', 'tg_username']


class PassportFilter(filters.FilterSet):
    owner = filters.NumberFilter(field_name='owner__id')

    class Meta:
        model = Passport
        fields = ['owner']


class OrderFilter(PriceRangeFilter):
    owner = filters.NumberFilter(field_name='owner__id')
    category = filters.NumberFilter(field_name='category__id')
    status = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateFilter(field_name='created_at', lookup_expr='gte')

    class Meta(PriceRangeFilter.Meta):
        model = Order
        fields = ['owner', 'category', 'status', 'created_at']


class ProposalFilter(PriceRangeFilter):
    owner = filters.NumberFilter(field_name='owner__id')
    order = filters.NumberFilter(field_name='order__id')
    status = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateFilter(field_name='created_at', lookup_expr='gte')

    class Meta(PriceRangeFilter.Meta):
        model = Proposal
        fields = ['owner', 'order', 'status', 'created_at']


class JobFilter(PriceRangeFilter):
    order = filters.NumberFilter(field_name='order__id')
    proposal = filters.NumberFilter(field_name='proposal__id')
    status = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    assignee = filters.NumberFilter(field_name='assignee__id')

    class Meta(PriceRangeFilter.Meta):
        model = Job
        fields = ['order', 'proposal', 'status', 'created_at', 'assignee']


class ReviewFilter(filters.FilterSet):
    job = filters.NumberFilter(field_name='job__id')
    owner = filters.NumberFilter(field_name='owner__id')
    whom = filters.NumberFilter(field_name='whom__id')
    rating = filters.NumberFilter()

    class Meta:
        model = Review
        fields = ['job', 'owner', 'whom', 'rating']


class AppealFilter(filters.FilterSet):
    job = filters.NumberFilter(field_name='job__id')
    owner = filters.NumberFilter(field_name='owner__id')
    whom = filters.NumberFilter(field_name='whom__id')
    to = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Appeal
        fields = ['job', 'owner', 'whom', 'to']
