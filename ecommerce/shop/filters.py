import django_filters
from django.db.models import Q
from .models import *

class ProductFilter(django_filters.FilterSet):
    color = django_filters.CharFilter(field_name='colors', lookup_expr='icontains')
    size = django_filters.CharFilter(field_name='sizes', lookup_expr='icontains')
    gender = django_filters.CharFilter(field_name='gender', lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.filter(deleted=False))
    sub_category = django_filters.ModelChoiceFilter(queryset=SubCategory.objects.filter(deleted=False))
    min_price = django_filters.NumberFilter(field_name='sale_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='sale_price', lookup_expr='lte')
    ordering = django_filters.OrderingFilter(
        fields=(
            ('sale_price', 'sale_price'),
            ('created_at', 'created_at'),
            ('name', 'name'),
        ),
        field_labels={
            'sale_price': 'Price',
            'created_at': 'Date',
            'name': 'Name',
        },
    )

    class Meta:
        model = Product
        fields = ['color', 'size', 'gender', 'category', 'sub_category', 'min_price', 'max_price']
