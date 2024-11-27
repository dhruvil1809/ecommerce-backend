from shop.views.utils import *
from django.db.models import Sum
from django.db import transaction
import razorpay
import os
from dotenv import load_dotenv

load_dotenv()


RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def update_best_sellers():
    # Count total orders for each product by summing quantity
    products_with_sales = (
        Product.objects
        .annotate(total_sales=Sum('orderitem__quantity'))
        .order_by('-total_sales')  # Sort in descending order based on total sales
    )
    
    # Get top 8 best sellers
    top_8_best_sellers = products_with_sales[:8]

    # Start a transaction to update the best seller field
    with transaction.atomic():
        # Set all products' best_seller field to False
        Product.objects.update(best_seller=False)
        
        # Set best_seller=True for the top 8 products
        for product in top_8_best_sellers:
            product.best_seller = True
            product.save()



class PaymentVerificationAPIView(APIView):
    def post(self, request):
        # Razorpay sends the signature, payment details, and order details
        payment_id = request.data.get('payment_id')
        order_id = request.data.get('order_id')
        signature = request.data.get('signature')

        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response(
                {
                    "errors": {
                        "order": "Order not found.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )

        payment = Payment.objects.get(payment_id=payment_id, order=order)

        # Razorpay's method to verify the signature
        generated_signature = razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        if generated_signature:
            payment.status = 'Completed'
            payment.save()

            # Update order status to 'Completed' upon successful payment
            order.status = 'Shipped'  # You can change the order status as per your workflow
            order.save()

            # Update best sellers after the payment is created
            update_best_sellers()

            return Response(
                    {
                        "message": "Payment successful.",
                        "status_code": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK
                )
    
        else:
            payment.status = 'Failed'
            payment.save()

            order_items = OrderItem.objects.filter(order=order)

            for item in order_items:
                # Increase the product stock back if payment fails
                product = item.product
                product.quantity += item.quantity
                product.save()


            # Update order status to 'Canceled' if payment fails
            order.status = 'Canceled'  # Change as needed in your workflow
            order.save()

            return Response(
                {
                    "errors": {
                        "payment": "Payment failed.",
                        "status_code": status.HTTP_200_OK
                    }
                },
                status=status.HTTP_200_OK,
            )
        