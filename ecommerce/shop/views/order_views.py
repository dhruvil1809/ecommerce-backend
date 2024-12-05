from shop.views.utils import *
import razorpay
import os
from dotenv import load_dotenv

load_dotenv()


RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))



class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        user = request.user

        # Fetch the user's cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "cart": "No cart found for this user.",
                        "status_code": status.HTTP_404_NOT_FOUND
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch the cart items
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items:
            return Response(
                {
                    "errors": {
                        "cart": "Cart is empty.",
                        "status_code": status.HTTP_400_BAD_REQUEST
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prepare the items data and calculate the total amount
        items_data = []
        total_quantity = 0
        total_amount = 0

        for item in cart_items:
            items_data.append({
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": item.product.sale_price,
                "size": item.size,
                "color": item.color
            })
            total_quantity += item.quantity
            total_amount += item.product.sale_price * item.quantity

        # Fetch the user's address(es)
        addresses = Address.objects.filter(user=user).order_by('-is_default')
        address_data = AddressSerializer(addresses, many=True).data

        
        # Prepare the user info
        user_info = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number
        }

        serializer = CartSerializer2(cart, context={'request': request})

        # Prepare the final checkout data
        checkout_data = {
            "user_info": user_info,
            "cart_items": serializer.data,
            "total_quantity": total_quantity,
            "total_amount": total_amount,
            "addresses": address_data
        }

        return Response(
            {
                "checkout_data": checkout_data,
                "message": "Checkout data fetched successfully.",
                "status_code": status.HTTP_200_OK
            },
            status=status.HTTP_200_OK
        )

class BuyNowAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        latest_cart_item = cart.items.order_by('-updated_at').first()
        
        if latest_cart_item:
            total_price = latest_cart_item.product.sale_price * latest_cart_item.quantity
            total_quantity = latest_cart_item.quantity
            
            latest_item_serializer = CartItemSerializer2(latest_cart_item, context={'request': request})
            latest_item_data = latest_item_serializer.data
        else:
            latest_item_data = None

        addresses = Address.objects.filter(user=request.user).order_by('-is_default')
        address_data = AddressSerializer(addresses, many=True).data

        items = {
            "items": [latest_item_data]
        }

        checkout_data ={
            "cart_items": items,
            "total_quantity":total_quantity,
            "total_amount": total_price,
            "addresses": address_data,
        }
        
        return Response(
            {
                "checkout_data": checkout_data,
                "message": "Cart retrieved successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = request.user
        
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)  
        size = request.data.get('size') 
        color = request.data.get('color')


        if not product_id:
            return Response(
                {
                    "errors": {
                        "product": "Product ID is required.",
                        "status_code": status.HTTP_400_BAD_REQUEST,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not quantity:
            return Response(
                {
                    "errors": {
                        "quantity": "Quantity is required.",
                        "status_code": status.HTTP_400_BAD_REQUEST,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not size:
            return Response(
                {
                    "errors": {
                        "size": "Size is required.",
                        "status_code": status.HTTP_400_BAD_REQUEST,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not color:
            return Response(
                {
                    "errors": {
                        "color": "Color is required.",
                        "status_code": status.HTTP_400_BAD_REQUEST,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(product_id=product_id)
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

        # Check if there is enough stock for the product
        if product.quantity < quantity:
            return Response(
                {
                    "errors": {
                        "product": f"Not enough stock for {product.name}.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )
        
        # Add or update the item in the user's cart
        cart, _ = Cart.objects.get_or_create(user=user)

        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            size=size,
            color=color
        ).first()

        if cart_item:
            # If the item exists, update the quantity
            cart_item.quantity = quantity
            cart_item.save()
        else:
            # If the item doesn't exist, create a new one
            CartItem.objects.create(
                cart=cart,
                product=product,
                size=size,
                color=color,
                quantity=quantity,
            )

        # Prepare the final checkout data
        product_data = {
            "product_id": product_id,
            "quantity": quantity,
            "size": size,
            "color": color
        }

        return Response(
            {
                "product_data": product_data,
                "message": "Product data fetched successfully.",
                "status_code": status.HTTP_200_OK
            },
            status=status.HTTP_200_OK
        )

class AddAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def post(self, request):
        user = request.user
        address_data = request.data

        # If the new address is marked as default, update the others to be non-default
        if address_data.get('is_default', True):
            # Update other addresses of the user to set is_default=False
            Address.objects.filter(user=user).update(is_default=False)

        serializer = AddressSerializer(data=address_data)
        if serializer.is_valid():
            # Save the new address
            serializer.save(user=user)
            return Response(
                {
                    "message": "Address added successfully.",
                    "address": serializer.data,
                    "status_code": status.HTTP_201_CREATED
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "errors": serializer.errors,
                "status_code": status.HTTP_400_BAD_REQUEST
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    

    def put(self, request, address_id):
        user = request.user
        address_data = request.data

        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return Response(
                {"message": "Address not found or does not belong to the user."},
                status=status.HTTP_404_NOT_FOUND
            )

        # If the new address is marked as default, update all other addresses to be non-default
        if address_data.get('is_default', True):
            # Set all other addresses of the user to is_default=False
            Address.objects.filter(user=user).exclude(id=address_id).update(is_default=False)

        serializer = AddressSerializer(address, data=address_data, partial=True)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                {
                    "message": "Address updated successfully.",
                    "address": serializer.data,
                    "status_code": status.HTTP_200_OK
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "errors": serializer.errors,
                "status_code": status.HTTP_400_BAD_REQUEST
            },
            status=status.HTTP_400_BAD_REQUEST
        )




class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def post(self, request):
        user = request.user

        # Fetch the user's cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "cart": "No cart found for this user.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )

        # Fetch the cart items
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items:
            return Response(
                {
                    "errors": {
                        "cart": "Cart is empty.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )

        # Prepare the items data and calculate total amount
        items_data = []
        total_amount = 0

        for item in cart_items:
            # Fetch the corresponding inventory entry
            try:
                inventory = Inventory.objects.get(
                    product=item.product, size=item.size
                )
            except Inventory.DoesNotExist:
                return Response(
                    {
                        "errors": {
                            "inventory": f"{item.size} size is not available for {item.product.name}.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            
            try:
                inventory = Inventory.objects.get(
                    product=item.product, color=item.color
                )
            except Inventory.DoesNotExist:
                return Response(
                    {
                        "errors": {
                            "inventory": f"{item.color} color is not available for {item.product.name}.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            # Check if there's enough stock
            if item.quantity > inventory.quantity:
                return Response(
                    {
                        "errors": {
                            "inventory": f"Not enough stock for {item.product.name}. Only {inventory.quantity} units available.",
                            "status_code": status.HTTP_200_OK,
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            items_data.append({
                "product": item.product.id,
                "quantity": item.quantity,
                "price": item.product.sale_price,
                "size": item.size,
                "color": item.color
            })
            total_amount += item.product.sale_price * item.quantity

        # If total_amount is provided in the request, use it instead of calculating
        total_amount_from_request = request.data.get('total_amount')
        if total_amount_from_request:
            total_amount = total_amount_from_request

        # Create the order in Razorpay
        razorpay_order = razorpay_client.order.create({
            "amount": int(total_amount * 100),  # Razorpay takes the amount in paise
            "currency": "INR",
            "payment_capture": 1
        })

        # Create the order in the database
        order = Order.objects.create(
            user=user,
            order_id=razorpay_order['id'],
            total_amount=total_amount
        )

        # Create the order items and update inventory
        for item in items_data:
            OrderItem.objects.create(
                order=order,
                product_id=item['product'],
                quantity=item['quantity'],
                size=item['size'],
                color=item['color'],
                price=item['price']
            )

            # Update inventory quantity
            inventory = Inventory.objects.get(
                product_id=item['product'], size=item['size'], color=item['color']
            )
            inventory.quantity -= item['quantity']
            inventory.save()

        order_data = {
            "order_id": razorpay_order['id'],
            "amount": total_amount,
            "currency": "INR",
            "key_id": RAZORPAY_KEY_ID
        }
        return Response(
            {
                "order_data": order_data,
                "message": "Order created successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )






class GetUserOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomRenderer]

    def get(self, request):
        user = request.user

        orders = Order.objects.filter(user=user).order_by('-created_at')
        
        if not orders:
            return Response(
                {
                    "errors": {
                        "orders": "No orders found for this user.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )

        serializer = OrderSerializer(orders, many=True, context={'request': request})

        return Response(
            {
                "orders": serializer.data,
                "status_code": status.HTTP_200_OK
            },
            status=status.HTTP_200_OK
        )