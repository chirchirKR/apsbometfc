from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import MpesaPayment


def send_payment_confirmation(payment_id):
    try:
        payment = MpesaPayment.objects.get(id=payment_id)

        # Get customer email
        email = payment.order.email

        if not email:
            return

        subject = "APS BOMET FC - Payment Confirmation"

        message = f"""
Hello {payment.order.customer_name},

Your payment has been received successfully!

PAYMENT DETAILS
-------------------------
Order Number: {payment.order.number}
Amount Paid: KES {payment.amount}
M-Pesa Receipt: {payment.mpesa_receipt}
Payment Date: {timezone.localtime(payment.created_at)}

Your payment details will be used on date of collection which you will be informed.

Thank you for shopping with APS BOMET FC.

Your support is highly appreciated!

APS BOMET FC
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

    except Exception:
        import logging
        logging.exception("Payment confirmation email failed.")