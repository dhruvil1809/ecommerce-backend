from django.urls import path
from shop.views import *

urlpatterns = [
    path('categories/', CategoryAPIView.as_view(), name='categories'),
    path('category-create/', CategoryAPIView.as_view(), name='category-create'),
    path('category-update/<slug:slug>', CategoryAPIView.as_view(), name='category-update'),

    path('sub-categories/', SubCategoryAPIView.as_view(), name='sub-categories'),
    path('sub-category-create/', SubCategoryAPIView.as_view(), name='sub-category-create'),
    path('sub-category-update/<slug:slug>', SubCategoryAPIView.as_view(), name='sub-category-update'),

    path('products/', ProductAPIView.as_view(), name='products'),
    path('product-create/', ProductAPIView.as_view(), name='product-create'),
    path('product-update/<slug:slug>', ProductAPIView.as_view(), name='product-update'),
]
