from rest_framework import serializers
from shop.models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    # def validate_name(self, value):
    #     if Category.objects.filter(name=value).exists():
    #         raise serializers.ValidationError("A category with this name already exists.")
    #     return value
    

class SubCategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    
    class Meta:
        model = SubCategory
        fields = '__all__'

    # def validate_name(self, value):
    #     if SubCategory.objects.filter(name=value).exists():
    #         raise serializers.ValidationError("A subcategory with this name already exists.")
    #     return value

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
        child=serializers.ImageField(), write_only=True, required=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'slug', 'description', 'regular_price',
            'sale_price', 'sizes', 'colors', 'category', 'sub_category',
            'gender', 'product_code', 'product_sku', 'tags', 'quantity', 'status',
            'created_at', 'updated_at', 'images', 'uploaded_images'
        ]

    # def validate_name(self, value):
    #     if Product.objects.filter(name=value).exists():
    #         raise serializers.ValidationError("A Product with this name already exists.")
    #     return value

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(**validated_data)
        
        # Save multiple images
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        
        return product