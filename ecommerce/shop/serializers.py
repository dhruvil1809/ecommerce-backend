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


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['id', 'color', 'size', 'quantity']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    is_liked_by_user = serializers.SerializerMethodField()
    inventory = InventorySerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'slug', 'description', 'regular_price',
            'sale_price', 'category', 'sub_category','average_rating','is_liked_by_user',
            'gender', 'product_code', 'product_sku', 'status', 'top_collection',
            'created_at', 'updated_at', 'images', 'uploaded_images', 'inventory'
        ]

    def get_is_liked_by_user(self, obj):
        """
        Returns True if the current user has liked the product; otherwise, False.
        """
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.liked_by.filter(id=user.id).exists()
        return False

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        inventory_data = validated_data.pop('inventory')
        product = Product.objects.create(**validated_data)
        
        # Save multiple images
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)

        for item in inventory_data:
            Inventory.objects.create(product=product, **item)
        
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        nventory_data = validated_data.pop('inventory')
        instance = super().update(instance, validated_data)
        
        if uploaded_images:
            # Optionally delete old images
            ProductImage.objects.filter(product=instance).delete()

            # Save new images
            for image in uploaded_images:
                ProductImage.objects.create(product=instance, image=image)

        if nventory_data:
            # Delete old inventory
            Inventory.objects.filter(product=instance).delete()

            # Save new inventory
            for item in nventory_data:
                Inventory.objects.create(product=instance, **item)

        return instance



class GetProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    sub_category = GetSubCategorySerializer(read_only=True)
    inventory = InventorySerializer(many=True, read_only=True)
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

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'size', 'color', 'created_at', 'updated_at']
        extra_kwargs = {'cart': {'required': False}}

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at', 'items']


class CartItemSerializer2(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'size', 'color']
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
    

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'size', 'color']  # Customize the fields as needed

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['order_id', 'status', 'total_amount', 'created_at', 'updated_at', 'items']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address', 'city', 'state', 'country', 'postal_code', 'first_name', 'last_name', 'phone_number', 'is_default']



