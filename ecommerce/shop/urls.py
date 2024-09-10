from django.urls import path
from shop.views import *

urlpatterns = [
    path('categories/', CategoryAPIView.as_view(), name='categories'),
    path('all-categories/', AllCategoryAPIView.as_view(), name='all-categories'),
    path('category-create/', CategoryAPIView.as_view(), name='category-create'),
    path('category-update/<slug:slug>', CategoryAPIView.as_view(), name='category-update'),
    path('category-delete/<slug:slug>', CategoryAPIView.as_view(), name='category-delete'),

    path('sub-categories/', SubCategoryAPIView.as_view(), name='sub-categories'),
    path('all-sub-categories/', AllSubCategoryAPIView.as_view(), name='all-sub-categories'),
    path('sub-category-create/', SubCategoryAPIView.as_view(), name='sub-category-create'),
    path('sub-category-update/<slug:slug>', SubCategoryAPIView.as_view(), name='sub-category-update'),
    path('sub-category-delete/<slug:slug>', SubCategoryAPIView.as_view(), name='sub-category-delete'),

    path('products/', ProductAPIView.as_view(), name='products'),
    path('all-products/', AllProductAPIView.as_view(), name='all-products'),
    path('product-create/', ProductAPIView.as_view(), name='product-create'),
    path('product-update/<slug:slug>', ProductAPIView.as_view(), name='product-update'),
    path('product-delete/<slug:slug>', ProductAPIView.as_view(), name='product-delete'),
]
