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
                            "status_code": status.HTTP_200_OK
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            
            if product.colors and color not in product.colors:
                return Response(
                    {
                        "errors": {
                            "color":f"Color {color} is not available for this product.",
                            "status_code": status.HTTP_200_OK
                        }
                    },
                    status=status.HTTP_200_OK,
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
                            "status_code": status.HTTP_200_OK
                        }
                    },
                    status=status.HTTP_200_OK,
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
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
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
                        "product":f"{product.quantity} units available in stock.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
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
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )
        
        if product.colors and color not in product.colors:
            return Response(
                {
                    "errors": {
                        "color":f"Color {color} is not available for this product.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )

        # Proceed with updating the cart item
        serializer = CartItemSerializer(cart_item, data=request.data, partial=True, context={'request': request})
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
