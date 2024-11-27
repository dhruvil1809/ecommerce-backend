from shop.views.utils import *
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from shop.views.utils import ProductFilter
from django.db.models import Avg, Min, Max


class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        products = Product.objects.filter(deleted=False)
        
        paginator = PageNumberPagination()
        paginator.page_size = 21

        paginated_products = paginator.paginate_queryset(products, request)

        serializer = GetProductSerializer(paginated_products, many=True, context={'request': request})

        return paginator.get_paginated_response(
            {
                "Products_data": serializer.data,
                "current_page": paginator.page.number,
                "page_size": paginator.page_size,
                "message": "Products retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )
    
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
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


        serializer = ProductSerializer(data=data, context={'request': request})
        category_id = request.data.get("category")
        sub_category_id = request.data.get("sub_category")
        name = request.data.get('name')

        if Product.objects.filter(name=name, deleted=False).exists():
            return Response(
                {
                    "errors": {
                        "name": "A Product with this name already exists.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        if not Category.objects.filter(id=category_id).exists():
            return Response(
                {
                    "errors": {
                        "category": "Category does not exist.", 
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        if not SubCategory.objects.filter(id=sub_category_id).exists():
            return Response(
                {
                    "errors": {
                        "sub_category": "SubCategory does not exist.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Product create successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
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
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        data = request.data.copy()  
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

        serializer = ProductSerializer(product, data=data, partial=True, context={'request': request})
        category_id = request.data.get("category")
        sub_category_id = request.data.get("sub_category")
        name = request.data.get('name')

        if Product.objects.filter(name=name, deleted=False).exclude(slug=slug).exists():
            return Response(
                {
                    "errors": {
                        "name": "A Product with this name already exists.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        if not Category.objects.filter(id=category_id).exists():
            return Response(
                {
                    "errors": {
                        "category": "Category does not exist.", 
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        if not SubCategory.objects.filter(id=sub_category_id).exists():
            return Response(
                {
                    "errors": {
                        "sub_category": "SubCategory does not exist.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
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
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
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

        serializer = GetProductSerializer(products, many=True, context={'request': request})

        return Response(
            {
                "Products_data": serializer.data,
                "message": "Products retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK
        )
    

class HomePageData(APIView):
    renderer_classes = [CustomRenderer]

    def get(self, request):

        categories = Category.objects.filter(add_to_home=True, deleted=False)
        categories_serializer = CategorySerializer(categories, many=True)

        products = Product.objects.filter(top_collection=True, deleted=False).order_by('-created_at')[:8]
        products_serializer = GetProductSerializer(products, many=True, context={'request': request})

        best_sellers = Product.objects.filter(best_seller=True).order_by('-updated_at')
        best_sellers_serializer = GetProductSerializer(best_sellers, many=True, context={'request': request})


        return Response(
                {
                    "categories": categories_serializer.data,
                    "top_collection": products_serializer.data,
                    "best_sellers": best_sellers_serializer.data,
                    "message": "Data retrieved successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK
            )
    

class ProductsByCategoryAPIView(APIView):
    renderer_classes = [CustomRenderer]

    def get(self, request, category_slug):
        try:
            category = Category.objects.get(slug=category_slug, deleted=False, status=True)
            products = Product.objects.filter(category=category, deleted=False, status=True)
        
            paginator = PageNumberPagination()
            paginator.page_size = 21

            paginated_categories = paginator.paginate_queryset(products, request)

            serializer = ProductSerializer(paginated_categories, many=True, context={'request': request})

            return paginator.get_paginated_response(
                {
                    "products": serializer.data,
                    "current_page": paginator.page.number,
                    "page_size": paginator.page_size,
                    "message": "Products retrieved successfully.",
                    "status_code": status.HTTP_200_OK,
                }
            )
    
        except Category.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "category": "Category not found.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )
        

class ProductBySlugAPIView(APIView):
    renderer_classes = [CustomRenderer]
    def get(self, request, product_slug):
        try:
            product = Product.objects.get(slug=product_slug, deleted=False, status=True)
            serializer = GetProductSerializer(product, context={'request': request})
            return Response(
                    {
                        "product": serializer.data,
                        "message": "Product retrieved successfully.",
                        "status_code": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK
                )
        except Product.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "product": "Product not found.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )
        

class ProductLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request, *args, **kwargs):
        user = request.user

        liked_products = Product.objects.filter(liked_by=user, deleted=False, status=True)
    
        paginator = PageNumberPagination()
        paginator.page_size = 20

        paginated_categories = paginator.paginate_queryset(liked_products, request)

        serializer = ProductSerializer(paginated_categories, many=True, context={'request': request})

        return paginator.get_paginated_response(
            {
                "product": serializer.data,
                "current_page": paginator.page.number,
                "page_size": paginator.page_size,
                "message": "Product retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )
        

    def post(self, request, product_slug):
        try:
            product = Product.objects.get(slug=product_slug, deleted=False, status=True)
            user = request.user

            if user in product.liked_by.all():
                product.liked_by.remove(user)  # Unlike the product
                liked = False
            else:
                product.liked_by.add(user)  # Like the product
                liked = True

            product.save()

            return Response(
                {
                    "message": "Product like status updated successfully.",
                    "liked": liked,
                    "status_code": status.HTTP_200_OK
                },
                status=status.HTTP_200_OK
            )
        except Product.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "product": "Product not found.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )
        



class ProductFilterView(generics.ListAPIView):
    renderer_classes = [CustomRenderer]
    queryset = Product.objects.filter(deleted=False, status=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        top_rated = self.request.query_params.get('top_rated', None)
        if top_rated:
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        return queryset
    
    def list(self, request, *args, **kwargs):
        # Get the filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        # Extract filter options from the current queryset
        sizes = list({size for sizes in queryset.values_list('sizes', flat=True) for size in (sizes or [])})
        colors = list({color for colors in queryset.values_list('colors', flat=True) for color in (colors or [])})
        genders = list({gender for gender in queryset.values_list('gender', flat=True) if gender})

        # Compute min_price and max_price from the filtered queryset
        min_price = queryset.aggregate(min_price=Min('sale_price'))['min_price']
        max_price = queryset.aggregate(max_price=Max('sale_price'))['max_price']

        # Add filter-related data to the response
        response.data['filters'] = {
            'sizes': sizes,
            'colors': colors,
            'genders': genders,
            'min_price': min_price,
            'max_price': max_price
        }
        return response
    
    def get_serializer(self, *args, **kwargs):
        # Pass the request context to the serializer
        kwargs['context'] = {'request': self.request}
        return super().get_serializer(*args, **kwargs)
    