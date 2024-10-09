from rest_framework import serializers
from shop.models import *


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


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'slug', 'description', 'regular_price',
            'sale_price', 'sizes', 'colors', 'category', 'sub_category',
            'gender', 'product_code', 'product_sku', 'tags', 'quantity', 'status',
            'created_at', 'updated_at', 'images', 'uploaded_images'
        ]

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(**validated_data)
        
        # Save multiple images
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        instance = super().update(instance, validated_data)
        
        if uploaded_images:
            # Optionally delete old images
            ProductImage.objects.filter(product=instance).delete()

            # Save new images
            for image in uploaded_images:
                ProductImage.objects.create(product=instance, image=image)

        return instance



class GetProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    sub_category = GetSubCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(slug_field='product_id', queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'size', 'color']
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