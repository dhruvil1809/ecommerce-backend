import json
from django.shortcuts import render
from shop.serializers import *
from ecommerce.renderers import CustomRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


class CategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        categories = Category.objects.filter(deleted=False)

        paginator = PageNumberPagination()
        paginator.page_size = 20

        paginated_categories = paginator.paginate_queryset(categories, request)

        serializer = CategorySerializer(paginated_categories, many=True)

        return paginator.get_paginated_response(
            {
                "categories_data": serializer.data,
                "message": "Categories retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        name = request.data.get('name')

        if Category.objects.filter(name=name, deleted=False).exists():
            return Response(
                {
                    "errors": {
                        "name": "A category with this name already exists.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Category create successfully.",
                    "status_code": status.HTTP_201_CREATED,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def put(self, request, slug):
        try:
            category = Category.objects.get(slug=slug, deleted=False)
        except Category.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "category": "Category not found.", 
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CategorySerializer(category, data=request.data, partial=True)
        name = request.data.get('name')

        if Category.objects.filter(name=name, deleted=False).exclude(slug=slug).exists():
            return Response(
                {
                    "errors": {
                        "name": "A category with this name already exists.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Category updated successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def delete(self, request, slug):
        try:
            category = Category.objects.get(slug=slug, deleted=False)
        except Category.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "category": "Category not found.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Soft delete
        category.deleted = True
        category.save()

        return Response(
            {
                "message": "Category deleted successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class AllCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]
    
    def get(self, request):
        categories = Category.objects.filter(deleted=False)

        serializer = CategorySerializer(categories, many=True)

        return Response(
            {
                "categories_data": serializer.data,
                "message": "Categories retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK
        )
    

class SubCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        sub_categories = SubCategory.objects.filter(deleted=False)

        paginator = PageNumberPagination()
        paginator.page_size = 20

        paginated_subcategories = paginator.paginate_queryset(sub_categories, request)

        serializer = GetSubCategorySerializer(paginated_subcategories, many=True)

        return paginator.get_paginated_response(
            {
                "subcategories_data": serializer.data,
                "message": "SubCategories retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )

    def post(self, request):
        serializer = SubCategorySerializer(data=request.data)
        category_id = request.data.get("category")
        name = request.data.get('name')

        if not Category.objects.filter(id=category_id).exists():
            return Response(
                {
                    "errors": {
                        "category": "Category does not exist.", 
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if SubCategory.objects.filter(name=name, deleted=False).exists():
            return Response(
                {
                    "errors": {
                        "name": "A subcategory with this name already exists.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "SubCategory create successfully.",
                    "status_code": status.HTTP_201_CREATED,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def put(self, request, slug):
        try:
            sub_category = SubCategory.objects.get(slug=slug, deleted=False)
        except SubCategory.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "category": "SubCategory not found.", 
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SubCategorySerializer(sub_category, data=request.data, partial=True)
        category_id = request.data.get("category")
        name = request.data.get('name')

        if not Category.objects.filter(id=category_id).exists():
            return Response(
                {
                    "errors": {
                        "category": "Category does not exist.", 
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if SubCategory.objects.filter(name=name, deleted=False).exclude(slug=slug).exists():
            return Response(
                {
                    "errors": {
                        "name": "A subcategory with this name already exists.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "SubCategory updated successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def delete(self, request, slug):
        try:
            sub_category = SubCategory.objects.get(slug=slug, deleted=False)
        except SubCategory.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "subcategory": "SubCategory not found.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Soft delete
        sub_category.deleted = True
        sub_category.save()

        return Response(
            {
                "message": "SubCategory deleted successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )
    
    
class AllSubCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        sub_categories = SubCategory.objects.filter(deleted=False)

        serializer = GetSubCategorySerializer(sub_categories, many=True)

        return Response(
            {
                "subcategories_data": serializer.data,
                "message": "SubCategories retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK
        )



class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        products = Product.objects.filter(deleted=False)
        
        paginator = PageNumberPagination()
        paginator.page_size = 20

        paginated_products = paginator.paginate_queryset(products, request)

        serializer = GetProductSerializer(paginated_products, many=True)

        return paginator.get_paginated_response(
            {
                "Products_data": serializer.data,
                "message": "Products retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )
    
    def post(self, request, *args, **kwargs):
        data = request.data
        sizes = data.get('sizes')
        if sizes:
            sizes_list = sizes.split(',')
            data['sizes'] = json.dumps(sizes_list)

        colors = data.get('colors')
        if colors:
            colors_list = colors.split(',')
            data['colors'] = json.dumps(colors_list)

        tags = data.get('tags')
        if tags:
            tags_list = tags.split(',')
            data['tags'] = json.dumps(tags_list)


        serializer = ProductSerializer(data=data)
        category_id = request.data.get("category")
        sub_category_id = request.data.get("sub_category")
        name = request.data.get('name')

        if Product.objects.filter(name=name, deleted=False).exists():
            return Response(
                {
                    "errors": {
                        "name": "A Product with this name already exists.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not Category.objects.filter(id=category_id).exists():
            return Response(
                {
                    "errors": {
                        "category": "Category does not exist.", 
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not SubCategory.objects.filter(id=sub_category_id).exists():
            return Response(
                {
                    "errors": {
                        "sub_category": "SubCategory does not exist.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Product create successfully.",
                    "status_code": status.HTTP_201_CREATED,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def put(self, request, slug):
        try:
            product = Product.objects.get(slug=slug, deleted=False)
        except Product.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "category": "Product not found.", 
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        data = request.data
        sizes = data.get('sizes')
        if sizes:
            sizes_list = sizes.split(',')
            data['sizes'] = json.dumps(sizes_list)

        colors = data.get('colors')
        if colors:
            colors_list = colors.split(',')
            data['colors'] = json.dumps(colors_list)

        tags = data.get('tags')
        if tags:
            tags_list = tags.split(',')
            data['tags'] = json.dumps(tags_list)

        serializer = ProductSerializer(product, data=data, partial=True)
        category_id = request.data.get("category")
        sub_category_id = request.data.get("sub_category")
        name = request.data.get('name')

        if Product.objects.filter(name=name, deleted=False).exclude(slug=slug).exists():
            return Response(
                {
                    "errors": {
                        "name": "A Product with this name already exists.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not Category.objects.filter(id=category_id).exists():
            return Response(
                {
                    "errors": {
                        "category": "Category does not exist.", 
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not SubCategory.objects.filter(id=sub_category_id).exists():
            return Response(
                {
                    "errors": {
                        "sub_category": "SubCategory does not exist.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                        }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Product updated successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def delete(self, request, slug):
        try:
            product = Product.objects.get(slug=slug, deleted=False)
        except Product.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "product": "Product not found.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Soft delete
        product.deleted = True
        product.save()

        return Response(
            {
                "message": "Product deleted successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )
    

class AllProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        products = Product.objects.filter(deleted=False)

        serializer = GetProductSerializer(products, many=True)

        return Response(
            {
                "Products_data": serializer.data,
                "message": "Products retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK
        )