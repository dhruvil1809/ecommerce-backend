from django.urls import path
from shop.views.product_views import *
from shop.views.category_views import *
from shop.views.cart_views import *
from shop.views.review_views import *
from shop.views.order_views import *
from shop.views.order_views import *
from shop.views.payment_views import *

urlpatterns = [
    path('categories/', CategoryAPIView.as_view(), name='categories'),
    path('all-categories/', AllCategoryAPIView.as_view(), name='all-categories'),
    path('category-create/', CategoryAPIView.as_view(), name='category-create'),
    path('category-update/<slug:slug>', CategoryAPIView.as_view(), name='category-update'),
    path('category-delete/<slug:slug>', CategoryAPIView.as_view(), name='category-delete'),

    path('sub-categories/', SubCategoryAPIView.as_view(), name='sub-categories'),
    path('all-sub-categories/', AllSubCategoryAPIView.as_view(), name='all-sub-categories'),
    path('subcategory-by-category/<slug:category_slug>/', SubCategoryByCategoryAPIView.as_view(), name='subcategory-by-category'),
    path('category-subcategory/', CategorySubcategoryListAPIView.as_view(), name='category-subcategory'),
    path('sub-category-create/', SubCategoryAPIView.as_view(), name='sub-category-create'),
    path('sub-category-update/<slug:slug>', SubCategoryAPIView.as_view(), name='sub-category-update'),
    path('sub-category-delete/<slug:slug>', SubCategoryAPIView.as_view(), name='sub-category-delete'),

    path('products/', ProductAPIView.as_view(), name='products'),
    path('all-products/', AllProductAPIView.as_view(), name='all-products'),
    path('product-create/', ProductAPIView.as_view(), name='product-create'),
    path('product-update/<slug:slug>', ProductAPIView.as_view(), name='product-update'),
    path('product-delete/<slug:slug>', ProductAPIView.as_view(), name='product-delete'),
    path('variant-delete/<int:id>', DeleteVariantApi.as_view(), name='variant-delete'),
    path('product-variant-filter/', ProductVariantFilterView.as_view(), name='product-variant-filter'),

    path('get-cart/', CartAPIView.as_view(), name='get-cart'),
    path('add-cart/', CartAPIView.as_view(), name='add-cart'),
    path('update-cart-item/<int:item_id>', CartItemAPIView.as_view(), name='update-cart-item'),
    path('delete-cart-item/<int:item_id>', CartItemAPIView.as_view(), name='delete-cart-item'),

    path('tags/', TagAPIView.as_view(), name='tag-list'),
    path('all-tags/', GetAllTagAPIView.as_view(), name='all-tag-list'),
    path('add-tag/', TagAPIView.as_view(), name='add-tag'),
    path('update-tag/<int:id>/', TagAPIView.as_view(), name='update-tag'),
    path('delete-tag/<int:id>/', TagAPIView.as_view(), name='delete-tag'),

    path('attributes/', AttributeAPIView.as_view(), name='attribute-list'),
    path('all-attributes/', GetAllAttributeAPIView.as_view(), name='all-attribute-list'),
    path('add-attribute/', AttributeAPIView.as_view(), name='add-attribute'),
    path('update-attribute/<int:id>/', AttributeAPIView.as_view(), name='update-attribute'),
    path('delete-attribute/<int:id>/', AttributeAPIView.as_view(), name='delete-attribute'),

    path('get-attribute-values/<int:attribute_id>/', AttributeValueAPIView.as_view(), name='attribute-value-by-attribute'),
    path('add-attribute-value/', AttributeValueAPIView.as_view(), name='add-attribute-value'),
    path('update-attribute-value/<int:id>/', AttributeValueAPIView.as_view(), name='update-attribute-value'),
    path('delete-attribute-value/<int:id>/', AttributeValueAPIView.as_view(), name='delete-attribute-value'),

    path('home-data/', HomePageData.as_view(), name='home-data'),
    path('products-by-category/<str:category_slug>/', ProductsByCategoryAPIView.as_view(), name='products-by-category'),
    path('product-by-slug/<str:product_slug>/', ProductBySlugAPIView.as_view(), name='product-by-slug'),
    path('product-like/<str:product_slug>/', ProductLikeAPIView.as_view(), name='product-like'),
    path('wishlist/', ProductLikeAPIView.as_view(), name='wishlist'),
    path('product-review/<int:product_id>/', ReviewAPIView.as_view(), name='product-review'),
    path('product-review-update/<int:product_id>/', ReviewAPIView.as_view(), name='product-review-update'),
    path('get-product-review/<int:product_id>/', ReviewAPIView.as_view(), name='get-product-review'),
    path('product-filter/', ProductFilterView.as_view(), name='product-filter'),

    # path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    # path('add-address/', AddAddressAPIView.as_view(), name='add-address'),
    # path('update-address/<int:address_id>/', AddAddressAPIView.as_view(), name='update-address'),
    # path('create-order/', CreateOrderAPIView.as_view(), name='create-order'),
    # path('buy-now/', BuyNowAPIView.as_view(), name='buy-now'),
    # path('checkout-buy-now/', BuyNowAPIView.as_view(), name='checkout-buy-now'),
    # path('get-order-details/', GetUserOrderAPIView.as_view(), name='get-order-details')
]
