from shop.views.utils import *


class CategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        categories = Category.objects.filter(deleted=False)

        paginator = PageNumberPagination()
        paginator.page_size = 2

        paginated_categories = paginator.paginate_queryset(categories, request)

        serializer = CategorySerializer(paginated_categories, many=True)

        return paginator.get_paginated_response(
            {
                "categories_data": serializer.data,
                "current_page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "page_size": paginator.page_size,
                "message": "Categories retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            }
        )
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        name = request.data.get('name')
        add_to_home = request.data.get('add_to_home', False)

        if Category.objects.filter(name=name, deleted=False).exists():
            return Response(
                {
                    "errors": {
                        "name": "A category with this name already exists.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        if add_to_home and Category.objects.filter(add_to_home=True, deleted=False).count() >= 6:
            return Response(
                {
                    "errors": {
                        "add_to_home": "You can only add up to 6 categories to the home.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Category create successfully.",
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
            category = Category.objects.get(slug=slug, deleted=False)
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

        serializer = CategorySerializer(category, data=request.data, partial=True)
        name = request.data.get('name')
        add_to_home = request.data.get('add_to_home', False)

        if Category.objects.filter(name=name, deleted=False).exclude(slug=slug).exists():
            return Response(
                {
                    "errors": {
                        "name": "A category with this name already exists.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        if add_to_home and Category.objects.filter(add_to_home=True, deleted=False).count() >= 6:
            return Response(
                {
                    "errors": {
                        "add_to_home": "You can only add up to 6 categories to the home.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
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
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
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
                "current_page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "page_size": paginator.page_size,
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
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        if SubCategory.objects.filter(name=name, deleted=False).exists():
            return Response(
                {
                    "errors": {
                        "name": "A subcategory with this name already exists.",
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
                    "message": "SubCategory create successfully.",
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
            sub_category = SubCategory.objects.get(slug=slug, deleted=False)
        except SubCategory.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "category": "SubCategory not found.", 
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )

        serializer = SubCategorySerializer(sub_category, data=request.data, partial=True)
        category_id = request.data.get("category")
        name = request.data.get('name')

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

        if SubCategory.objects.filter(name=name, deleted=False).exclude(slug=slug).exists():
            return Response(
                {
                    "errors": {
                        "name": "A subcategory with this name already exists.",
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
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
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


class SubCategoryByCategoryAPIView(APIView):
    renderer_classes = [CustomRenderer]

    def get(self, request, category_slug):
        try:
            category = Category.objects.get(slug=category_slug, deleted=False)

            subcategories = SubCategory.objects.filter(category=category, deleted=False, status=True)

            serializer = SubCategorySerializer(subcategories, many=True)

            return Response({
                "category": category.name,
                "subcategories": serializer.data,
                "message": "Subcategories retrieved successfully.",
                "status_code": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)
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
        


class CategorySubcategoryListAPIView(APIView):
    renderer_classes = [CustomRenderer]

    def get(self, request):
        # Query categories and subcategories
        categories = Category.objects.filter(deleted=False, status=True).values('name', 'slug')
        subcategories = SubCategory.objects.filter(deleted=False, status=True).values('name', 'slug', 'category_id')

        # Organize subcategories under their parent categories
        category_data = []
        for category in categories:
            category_data.append({
                'name': category['name'],
                'slug': category['slug'],
                'subcategories': [
                    {'slug': sub['slug'],'name': sub['name']}
                    for sub in subcategories if sub['category_id'] == Category.objects.get(name=category['name']).id
                ]
            })

        return Response(
            {
                "categories": category_data,
                "message": "Categories and subcategories retrieved successfully.",
                "status_code": status.HTTP_200_OK
            },
            status=status.HTTP_200_OK
        )