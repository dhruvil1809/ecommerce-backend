from shop.views.utils import *
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
                "current_page": paginator.page.number,
                "page_size": paginator.page_size,
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
