from collections import defaultdict
from django.db.models import Count
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

        try:
            product = Product.objects.get(id=product_id, deleted=False)
        except:
            return Response(
                {
                    "errors": {
                        "error": "Product does not exist.", 
                        "status_code": status.HTTP_200_OK
                        }
                },
                status=status.HTTP_200_OK,
            )
        
        # Check if the user has ordered the product with status 'Delivered'
        review_permission = OrderItem.objects.filter(
            order__user=request.user,
            order__status="Delivered",
            product=product
        ).exists()


        has_review = Review.objects.filter(product=product, user=request.user).exists()

        if has_review:
            review_permission = False

        
        reviews = Review.objects.filter(product=product).order_by('-created_at')
        
        paginator = PageNumberPagination()
        paginator.page_size = 10

        paginated_categories = paginator.paginate_queryset(reviews, request)

        serializer = ReviewSerializer(paginated_categories, many=True)

        # Calculate rating distribution
        rating_counts = (
            reviews.values("rating")
            .annotate(count=Count("rating"))
            .order_by("-rating")
        )
        rating_map = {5: "Excellent", 4: "VeryGood", 3: "Good", 2: "Average", 1: "Poor"}
        rating_summary = defaultdict(int)
        for data in rating_counts:
            rating_summary[rating_map[data["rating"]]] = data["count"]

        # Fill missing ratings with 0
        for key in rating_map.values():
            rating_summary[key] = rating_summary.get(key, 0)

        return paginator.get_paginated_response(
            {
                "product": product.name,
                "reviews": serializer.data,
                "review_permission": review_permission,
                "rating_summary": dict(rating_summary),
                "current_page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,
                "page_size": paginator.page_size,
                "status_code": status.HTTP_200_OK,
            }
        )

    def post(self, request, product_id):

        try:
            product = Product.objects.get(id=product_id, deleted=False)
        except:
            return Response(
                {
                    "errors": {
                        "error": "Product does not exist.", 
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
                        "error": "You can only review products you have ordered.",
                        "status_code": status.HTTP_200_OK
                        } 
                },
                status=status.HTTP_200_OK,
            )
        
        
        # Check if the user has already reviewed the product
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response(
                {"errors": {
                    "error": "You have already reviewed this product.",
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
                        "error": "Rating must be between 1 and 5.",
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
                        "error": "Review does not exist for this product by the current user.",
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
                    "error": "Product does not exist.",
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
                        "error": "You can only update reviews for products you have ordered.",
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
                        "error": "Rating must be between 1 and 5.",
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
