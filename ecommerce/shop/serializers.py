from rest_framework import serializers
from shop.models.address_models import *
from shop.models.product_models import *
from shop.models.pyment_models import *
from shop.models.cart_models import *
from shop.models.category_models import *
from shop.models.order_models import *
from shop.models.review_models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
    

class SubCategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    
    class Meta:
        model = SubCategory
        fields = '__all__'


class GetSubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = SubCategory
        fields = '__all__'


class UpdateAttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ['id', 'var_title', 'color_code']
        read_only_fields = ['attribute']

class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute', 'var_title', 'color_code']

class AttributeSerializer(serializers.ModelSerializer):
    values = AttributeValueSerializer(many=True, read_only=True, source='filtered_values')

    class Meta:
        model = Attribute
        fields = ['id', 'var_title', 'values']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'var_title', 'deleted']


class VariantAttributeSerializer(serializers.ModelSerializer):
    var_title = serializers.CharField(source='attribute.var_title', read_only=True)
    value = serializers.SerializerMethodField()
    attribute_id = serializers.CharField(source='attribute.id', read_only=True)

    class Meta:
        model = VariantAttribute
        fields = ['id', 'attribute_id', 'var_title', 'value']

    def get_value(self, obj):
        value_data = {
            "id": str(obj.value.id),  # Convert to string if needed
            "var_title": obj.value.var_title,
            "color_code": obj.value.color_code if obj.value.color_code else None,
            "attribute_name": obj.attribute.var_title,
            "attribute_id": str(obj.attribute.id),  # Include attribute_id from var_title
        }
        return value_data

class VariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = ['id', 'image']

class VariantSerializer(serializers.ModelSerializer):
    variant_attributes = VariantAttributeSerializer(many=True, required=False)
    variant_images = VariantImageSerializer(many=True, required=False)

    class Meta:
        model = Variant
        fields = [
            'id', 'product_code', 'product_sku', 'quantity',
            'regular_price', 'sale_price', 'product_details', 'product_descriptions', 'variant_attributes', 'variant_images'
        ]


class ProductSerializer(serializers.ModelSerializer):
    is_liked_by_user = serializers.SerializerMethodField()
    variants = VariantSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'slug', 'category', 'sub_category','average_rating','is_liked_by_user',
            'gender', 'top_collection', 'in_stock', 'status', 'tags',
            'created_at', 'updated_at', 'variants', 'has_variants'
        ]

    def get_is_liked_by_user(self, obj):
        """
        Returns True if the current user has liked the product; otherwise, False.
        """
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.liked_by.filter(id=user.id).exists()
        return False

#     # def create(self, validated_data):
#     #     product = Product.objects.create(**validated_data)

#     #     return product

#     # def update(self, instance, validated_data):
#     #     uploaded_images = validated_data.pop('uploaded_images', [])
#     #     instance = super().update(instance, validated_data)
        
#     #     if uploaded_images:
#     #         # Optionally delete old images
#     #         ProductImage.objects.filter(product=instance).delete()

#     #         # Save new images
#     #         for image in uploaded_images:
#     #             ProductImage.objects.create(product=instance, image=image)

#     #     return instance



class GetProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    sub_category = GetSubCategorySerializer() 
    tags = TagSerializer(many=True, read_only=True)
    variants = VariantSerializer(many=True,read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_is_liked_by_user(self, obj):
        """
        Returns True if the current user has liked the product; otherwise, False.
        """
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.liked_by.filter(id=user.id).exists()
        return False

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(slug_field='product_id', queryset=Product.objects.all())
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'variant', 'created_at', 'updated_at']
        extra_kwargs = {'cart': {'required': False}}

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at', 'items']


class CartItemSerializer2(serializers.ModelSerializer):
    product = GetProductSerializer()
    variant = VariantSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'variant']
        extra_kwargs = {'cart': {'required': False}}

class CartSerializer2(serializers.ModelSerializer):
    items = CartItemSerializer2(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at', 'items']


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image']


class ReviewSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    profile_picture = serializers.ImageField(source="user.profile_picture", required=False)
    user = serializers.StringRelatedField(read_only=True)
    product = serializers.StringRelatedField(read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user', 'rating', 'review', 'images', 
            'created_at', 'updated_at', 'uploaded_images', 'first_name', 'last_name', 'profile_picture'
        ]

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        review = Review.objects.create(**validated_data)
        
        for image in uploaded_images:
            ReviewImage.objects.create(review=review, image=image)
        
        return review

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        instance = super().update(instance, validated_data)
        
        if uploaded_images:
            ReviewImage.objects.filter(review=instance).delete()

            for image in uploaded_images:
                ReviewImage.objects.create(review=instance, image=image)

        return instance
    

# class OrderItemSerializer(serializers.ModelSerializer):
#     product = GetProductSerializer(read_only=True)
#     class Meta:
#         model = OrderItem
#         fields = ['product', 'quantity', 'price', 'size', 'color']  # Customize the fields as needed

# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True)

#     class Meta:
#         model = Order
#         fields = ['order_id', 'status', 'total_amount', 'created_at', 'updated_at', 'items']


# class AddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = ['id', 'address', 'city', 'state', 'country', 'postal_code', 'first_name', 'last_name', 'phone_number', 'is_default']



