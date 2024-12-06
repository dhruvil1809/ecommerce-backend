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
        quantity = int(item_data.get('quantity', 1))
        size = item_data.get('size')
        color = item_data.get('color')

        try:
            product = Product.objects.get(product_id=product_id)

            # Find the matching inventory entry
            try:
                inventory = Inventory.objects.get(product=product, size=size)
            except Inventory.DoesNotExist:
                return Response(
                    {
                        "errors": {
                            "inventory": f"{size} size is not available.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            
            try:
                inventory = Inventory.objects.get(product=product, color=color)
            except Inventory.DoesNotExist:
                return Response(
                    {
                        "errors": {
                            "inventory": f"{color} size is not available.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            # Check if requested quantity exceeds available stock
            main_inventory = Inventory.objects.get(product=product, color=color, size=size)
            if quantity > main_inventory.quantity:
                return Response(
                    {
                        "errors": {
                            "inventory": f"Only {inventory.quantity} units are available in stock.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            # Check if the cart item with the same size and color already exists
            try:
                cart_item = CartItem.objects.get(
                    cart=cart,
                    product=product,
                    size=size,
                    color=color,
                )

                # Update the cart item with the new total quantity
                total_quantity = cart_item.quantity + quantity

                # Ensure total quantity does not exceed available stock
                if total_quantity > inventory.quantity:
                    available = inventory.quantity - cart_item.quantity
                    if available > 0:
                        return Response(
                            {
                                "errors": {
                                    "inventory": f"Only {available} additional units can be added.",
                                    "status_code": status.HTTP_200_OK,
                                }
                            },
                            status=status.HTTP_200_OK,
                        )
                    
                    return Response(
                        {
                            "errors": {
                                "inventory": f"0 units available in stock.",
                                "status_code": status.HTTP_200_OK
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
                    item_serializer.save(cart=cart, product=product)
                else:
                    return Response(
                        {"errors": item_serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Product.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "product": "Product not found.",
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
                        "product": "Cart item not found.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )

        # Get the product linked to the cart item
        product = cart_item.product

        # Fetch the requested updates
        new_quantity = int(request.data.get('quantity', cart_item.quantity))
        size = request.data.get('size', cart_item.size)
        color = request.data.get('color', cart_item.color)

        # Find the corresponding inventory entry
        try:
            inventory = Inventory.objects.get(product=product, size=size)
        except Inventory.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "inventory": f"{size} size is not available.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )
        
        try:
            inventory = Inventory.objects.get(product=product, color=color)
        except Inventory.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "inventory": f"{color} color is not available.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )

        # Check if the updated quantity exceeds available stock
        main_inventory = Inventory.objects.get(product=product, color=color, size=size)
        if new_quantity > main_inventory.quantity:
            return Response(
                {
                    "errors": {
                        "inventory": f"Only {inventory.quantity} units are available in stock.",
                        "status_code": status.HTTP_400_BAD_REQUEST,
                    }
                },
                status=status.HTTP_200_OK,
            )

        # Update cart item with validated data
        data = {
            "quantity": new_quantity,
            "size": size,
            "color": color,
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
                        "product": "Cart item not found.",
                        "status_code": status.HTTP_200_OK,
                    }
                },
                status=status.HTTP_200_OK,
            )






