from shop.views.utils import *


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer2(cart, context={'request': request})
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
        variant_id = item_data.get('variant')
        quantity = int(item_data.get('quantity', 1))

        try:
            product = Product.objects.get(product_id=product_id)
            variant = Variant.objects.get(id=variant_id, product=product)

            try:
                variant = Variant.objects.get(id=variant_id, product=product)
            except Variant.DoesNotExist:
                return Response(
                    {
                        "errors": {
                            "error": "Variant not found for the selected product.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            

            # Check if the requested quantity exceeds the available stock
            if quantity > variant.quantity:
                return Response(
                    {
                        "errors": {
                            "error": f"Only {variant.quantity} units are available in stock.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            # Check if the cart item with the same variant already exists
            try:
                cart_item = CartItem.objects.get(cart=cart, product=product, variant=variant)

                total_quantity = cart_item.quantity + quantity

                if total_quantity > variant.quantity:
                    available = variant.quantity - cart_item.quantity
                    if available > 0:
                        return Response(
                            {
                                "errors": {
                                    "error": f"Only {available} additional units can be added.",
                                    "status_code": status.HTTP_200_OK,
                                }
                            },
                            status=status.HTTP_200_OK,
                        )

                    return Response(
                        {
                            "errors": {
                                "error": f"0 units available in stock.",
                                "status_code": status.HTTP_200_OK,
                            }
                        },
                        status=status.HTTP_200_OK,
                    )

                cart_item.quantity = total_quantity
                cart_item.save()

            except CartItem.DoesNotExist:
                # Create a new cart item
                item_data['cart'] = cart.id
                item_serializer = CartItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    item_serializer.save(cart=cart, product=product, variant=variant)
                else:
                    return Response(
                        {"errors": item_serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Product.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Product not found.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "Cart updated successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )




class CartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def put(self, request, item_id):
        try:
            # Fetch the cart item
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Cart item not found.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )

        # Get the product linked to the cart item
        product = cart_item.product

        # Fetch the requested updates
        new_quantity = int(request.data.get('quantity', cart_item.quantity))
        variant_id = request.data.get('variant')

        # Find the corresponding variant
        try:
            variant = Variant.objects.get(id=variant_id, product=product)
        except Variant.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": f"Variant with id {variant_id} is not available for this product.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )
        

        # Check if the updated quantity exceeds available stock of the variant
        if new_quantity > variant.quantity:
            return Response(
                {
                    "errors": {
                        "error": f"Only {variant.quantity} units are available in stock for this variant.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )


        # Update cart item with validated data
        data = {
            "quantity": new_quantity,
            "variant": variant.id,
        }

        serializer = CartItemSerializer(cart_item, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Cart item updated successfully.",
                    "cart_item": serializer.data,
                    "status_code": status.HTTP_200_OK,  
                },
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {"errors": serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, item_id):
        try:
            # Fetch the cart item
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)

            # Delete the cart item
            cart_item.delete()
            return Response(
                {
                    "message": "Cart item removed successfully.",
                    "status_code": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        except CartItem.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "error": "Cart item not found.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )






