from shop.views.utils import *
import razorpay
import os
from dotenv import load_dotenv

load_dotenv()


RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


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
                        "product": "No cart found for this user.",
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
                        "product": "Cart is empty.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )

        # Prepare the items data and calculate total amount
        items_data = []
        total_amount = 0

        # Check if products have enough stock
        for item in cart_items:
            if item.product.quantity < item.quantity:
                return Response(
                    {
                        "errors": {
                            "product": f"Not enough stock for {item.product.name}.",
                            "status_code": status.HTTP_200_OK
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            items_data.append({
                "product": item.product.id,  # Assuming 'id' is used as the product ID
                "quantity": item.quantity,
                "price": item.product.sale_price,  # Assuming product has a 'price' field
                "size": item.size,
                "color": item.color
            })
            total_amount += item.product.sale_price * item.quantity

        # If total_amount is provided in the request, use it instead of calculating
        total_amount_from_request = request.data.get('total_amount')
        if total_amount_from_request:
            total_amount = total_amount_from_request  # Use the provided total_amount if exists

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

        # Create the order items
        for item in items_data:
            OrderItem.objects.create(
                order=order,
                product_id=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )

            # Update product quantity
            product = Product.objects.get(id=item['product'])
            product.quantity -= item['quantity']
            product.save()

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
            status=status.HTTP_200_OK
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