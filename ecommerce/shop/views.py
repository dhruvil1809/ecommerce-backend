import json
from django.shortcuts import get_object_or_404, render
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


        serializer = ProductSerializer(data=data)
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

        serializer = ProductSerializer(product, data=data, partial=True)
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

        serializer = GetProductSerializer(products, many=True)

        return Response(
            {
                "Products_data": serializer.data,
                "message": "Products retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK
        )
    

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer2(cart)
        return Response(
            {
                "cart_data": serializer.data,
                "message": "Cart retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        item_data = request.data

        product_id = item_data.get('product')
        quantity = item_data.get('quantity', 1)
        size = item_data.get('size')
        color = item_data.get('color')

        try:
            product = Product.objects.get(product_id=product_id)
            
            # Check if the size and color match the available options (if sizes/colors are defined)
            if product.sizes and size not in product.sizes:
                return Response(
                    {
                        "errors": {
                            "size":f"Size {size} is not available for this product.",
                            "status_code": status.HTTP_400_BAD_REQUEST
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            if product.colors and color not in product.colors:
                return Response(
                    {
                        "errors": {
                            "color":f"Color {color} is not available for this product.",
                            "status_code": status.HTTP_400_BAD_REQUEST
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cart_item = CartItem.objects.get(
                cart=cart,
                product_id=product_id,
                size=size if size else None,
                color=color if color else None
            )
            
            # Calculate the total quantity in cart (existing + new)
            total_quantity = cart_item.quantity + quantity

            # Check if the total quantity exceeds available stock
            if total_quantity > product.quantity:
                return Response(
                    {
                        "errors": {
                            "product": f"Only {product.quantity - cart_item.quantity} units available in stock.",
                            "status_code": status.HTTP_400_BAD_REQUEST
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update cart item with new total quantity
            cart_item.quantity = total_quantity
            cart_item.save()

        except CartItem.DoesNotExist:
            item_data['cart'] = cart.id
            item_serializer = CartItemSerializer(data=item_data)
            if item_serializer.is_valid():
                item_serializer.save(cart=cart)
            else:
                return Response(
                    {"errors": item_serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response({"message": "Cart updated successfully"}, status=status.HTTP_200_OK)


class CartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def put(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "product": "Cart item not found.",
                        "status_code": status.HTTP_404_NOT_FOUND
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get the product linked to the cart item
        product = cart_item.product

        # Get the quantity being updated from the request data
        new_quantity = request.data.get('quantity', cart_item.quantity)

        # Check if the requested quantity is greater than the available stock
        if new_quantity > product.quantity:
            return Response(
                {
                    "errors": {
                        "product":f"Only {product.quantity} units available in stock.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If size or color are being updated, ensure they are available
        size = request.data.get('size', cart_item.size)
        color = request.data.get('color', cart_item.color)

        # Check if the size and color match the available options (if sizes/colors are defined)
        if product.sizes and size not in product.sizes:
            return Response(
                {
                    "errors": {
                        "size":f"Size {size} is not available for this product.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if product.colors and color not in product.colors:
            return Response(
                {
                    "errors": {
                        "color":f"Color {color} is not available for this product.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Proceed with updating the cart item
        serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Cart item updated successfully.",
                    "cart_item": serializer.data,
                    "status_code": status.HTTP_200_OK
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)

            # Delete the cart item
            cart_item.delete()
            return Response(
                {
                    "message": "Cart item removed successfully.",
                    "status_code": status.HTTP_200_OK
                },
                status=status.HTTP_200_OK
            )
        except CartItem.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "product": "Cart item not found.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )


class HomePageData(APIView):
    renderer_classes = [CustomRenderer]

    def get(self, request):

        categories = Category.objects.filter(add_to_home=True, deleted=False)
        categories_serializer = CategorySerializer(categories, many=True)

        products = Product.objects.filter(top_collection=True, deleted=False).order_by('-created_at')[:8]
        products_serializer = GetProductSerializer(products, many=True)

        return Response(
                {
                    "categories": categories_serializer.data,
                    "top_collection": products_serializer.data,
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
            serializer = ProductSerializer(products, many=True)
            return Response(
                    {
                        "products": serializer.data,
                        "message": "Products retrieved successfully.",
                        "status_code": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK
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
            serializer = ProductSerializer(product)
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
        


from django.db.models import Q

def has_user_ordered_product(user, product):
    """Check if the user has ordered the product."""
    return OrderItem.objects.filter(
        order__user=user, 
        product=product, 
        order__status__in=['Shipped', 'Delivered']
    ).exists()



class ReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request, product_id):

        product = Product.objects.get(id=product_id, deleted=False)

        if not product:
            return Response(
                {
                    "errors": {
                        "product": "Product does not exist.", 
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        reviews = Review.objects.filter(product=product).order_by('-created_at')
        
        paginator = PageNumberPagination()
        paginator.page_size = 10

        paginated_categories = paginator.paginate_queryset(reviews, request)

        serializer = ReviewSerializer(paginated_categories, many=True)

        return paginator.get_paginated_response(
            {
                "product": product.name,
                "reviews": serializer.data,
                "status_code": status.HTTP_200_OK,
            }
        )

    def post(self, request, product_id):

        product = Product.objects.get(id=product_id, deleted=False)

        if not product:
            return Response(
                {
                    "errors": {
                        "product": "Product does not exist.", 
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        # Check if the user has ordered the product
        if not has_user_ordered_product(request.user, product):
            return Response(
                {
                    "errors": {
                        "authorization": "You can only review products you have ordered.",
                        "status_code": status.HTTP_200_OK
                        } 
                },
                status=status.HTTP_200_OK,
            )
        
        
        # Check if the user has already reviewed the product
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response(
                {"errors": {
                    "review": "You have already reviewed this product.",
                    "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )

        
        data = request.data.copy()

        rating = data.get('rating')
        if int(rating) < 1 or int(rating) > 5:
            return Response(
                {
                    "errors": {
                        "rating": "Rating must be between 1 and 5.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        data['product'] = product.id
        data['user'] = request.user.id
        
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(product=product, user=request.user)
            return Response(
                {
                    **serializer.data,
                    "message": "Review add successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )
    

    def put(self, request, product_id):
        try:
            review = Review.objects.get(product__id=product_id, user=request.user, product__deleted=False)
        except Review.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "review": "Review does not exist for this product by the current user.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )
        
        try:
            product = Product.objects.get(id=product_id, deleted=False)
        except Product.DoesNotExist:
            return Response(
                {
                    "errors": {
                    "product": "Product does not exist.",
                    "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )
        
        # Check if the user has ordered the product
        if not has_user_ordered_product(request.user, product):
            return Response(
                {
                    "errors": {
                        "authorization": "You can only update reviews for products you have ordered.",
                        "status_code": status.HTTP_200_OK
                        } 
                },
                status=status.HTTP_200_OK,
            )
        
        data = request.data.copy()

        rating = data.get('rating')
        if int(rating) < 1 or int(rating) > 5:
            return Response(
                {
                    "errors": {
                        "rating": "Rating must be between 1 and 5.",
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        serializer = ReviewSerializer(review, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    **serializer.data,
                    "message": "Review updated successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )
