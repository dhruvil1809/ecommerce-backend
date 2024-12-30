import json
from django.shortcuts import get_object_or_404, render
from shop.serializers import *
from ecommerce.renderers import CustomRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
import django_filters
from shop.models.address_models import *
from shop.models.product_models import *
from shop.models.pyment_models import *
from shop.models.cart_models import *
from shop.models.category_models import *
from shop.models.order_models import *
from shop.models.review_models import *


# class ProductFilter(django_filters.FilterSet):
#     color = django_filters.CharFilter(method='filter_color')
#     size = django_filters.CharFilter(method='filter_size')
#     gender = django_filters.CharFilter(field_name='gender', lookup_expr='iexact')
#     category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
#     sub_category = django_filters.CharFilter(field_name='sub_category__slug', lookup_expr='iexact')
    # min_price = django_filters.NumberFilter(field_name='sale_price', lookup_expr='gte')
    # max_price = django_filters.NumberFilter(field_name='sale_price', lookup_expr='lte')
    # ordering = django_filters.OrderingFilter(
    #     fields=(
    #         ('sale_price', 'sale_price'),
    #         ('created_at', 'created_at'),
    #         ('name', 'name'),
    #     ),
    #     field_labels={
    #         'sale_price': 'Price',
    #         'created_at': 'Date',
    #         'name': 'Name',
    #     },
    # )

#     class Meta:
#         model = Product
#         fields = ['color', 'size', 'gender', 'category', 'sub_category', 'min_price', 'max_price']

#     def filter_color(self, queryset, name, value):
#         return queryset.filter(inventory__color__icontains=value)

#     def filter_size(self, queryset, name, value):
#         return queryset.filter(inventory__size__icontains=value)


import django_filters
from django.db.models import Q

class ProductFilter(django_filters.FilterSet):
    # Standard Filters
    gender = django_filters.CharFilter(field_name='gender', lookup_expr='iexact')
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    sub_category = django_filters.CharFilter(field_name='sub_category__slug', lookup_expr='iexact')
    min_price = django_filters.NumberFilter(field_name='variants__sale_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='variants__sale_price', lookup_expr='lte')

    # Filters for VariantAttribute
    attribute = django_filters.CharFilter(
        field_name='variants__variant_attributes__attribute__var_title', lookup_expr='iexact'
    )
    value = django_filters.CharFilter(
        field_name='variants__variant_attributes__value__var_title', lookup_expr='iexact'
    )

    ordering = django_filters.OrderingFilter(
        fields=(
            ('variants__sale_price', 'sale_price'),
            ('created_at', 'created_at'),
            ('name', 'name'),
        ),
        field_labels={
            'variants__sale_price': 'Price',
            'created_at': 'Date',
            'name': 'Name',
        },
    )

    class Meta:
        model = Product
        fields = ['gender','category', 'sub_category', 'min_price', 'max_price', 'ordering', 'attribute', 'value']

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).distinct()

