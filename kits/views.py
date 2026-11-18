import json
import re
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required

from .models import Product, Order, OrderItem, MpesaPayment
from .cart import get_cart, save_cart, cart_details
from .daraja import stk_push, stk_query
from .email import *
import logging

logger = logging.getLogger(__name__)

def _normalise_phone(raw):
    digits = re.sub(r"\D", "", raw or "")
    if digits.startswith("0") and len(digits) == 10:
        digits = "254" + digits[1:]
    elif digits.startswith("7") and len(digits) == 9:
        digits = "254" + digits
    elif digits.startswith("1") and len(digits) == 9:
        digits = "254" + digits
    if not re.fullmatch(r"254[17]\d{8}", digits):
        raise ValueError("Enter a valid Kenyan M-Pesa number, e.g. 0712345678.")
    return digits


def catalogue(request):
    products = Product.objects.filter(active=True)
    return render(request, "kits/catalogue.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)
    return render(request, "kits/product_detail.html", {"product": product})


@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)
    try:
        quantity = int(request.POST.get("quantity", 1))
        size = request.POST.get("size", "").strip()
        if quantity < 1 or quantity > 20:
            raise ValueError
        if size not in product.size_list:
            raise ValueError
        if product.stock < quantity:
            messages.error(request, "Not enough stock is available for that quantity.")
            return redirect("kits:product_detail", pk=pk)
    except ValueError:
        messages.error(request, "Choose a valid size and quantity.")
        return redirect("kits:product_detail", pk=pk)
    cart = get_cart(request)
    key = f"{product.pk}:{size}"
    current = int(cart.get(key, {}).get("quantity", 0))
    if current + quantity > product.stock:
        messages.error(request, "That quantity exceeds available stock.")
        return redirect("kits:product_detail", pk=pk)
    cart[key] = {"product_id": product.pk, "size": size, "quantity": current + quantity}
    save_cart(request, cart)
    messages.success(request, "Kit added to your bag.")
    return redirect("kits:cart")


def cart_view(request):
    rows, total = cart_details(request)
    return render(request, "kits/cart.html", {"rows": rows, "total": total})


@require_POST
def update_cart(request, key):
    cart = get_cart(request)
    if key in cart:
        try:
            qty = int(request.POST.get("quantity", 1))
            product = Product.objects.get(pk=cart[key]["product_id"], active=True)
            if qty < 1:
                cart.pop(key)
            elif qty <= product.stock and qty <= 20:
                cart[key]["quantity"] = qty
            else:
                messages.error(request, "Requested quantity is above available stock.")
        except (ValueError, Product.DoesNotExist):
            cart.pop(key, None)
        save_cart(request, cart)
    return redirect("kits:cart")


@require_POST
def remove_from_cart(request, key):
    cart = get_cart(request)
    cart.pop(key, None)
    save_cart(request, cart)
    return redirect("kits:cart")

#@login_required
def checkout(request):
    rows, total = cart_details(request)
    if not rows:
        messages.info(request, "Your shopping bag is empty.")
        return redirect("kits:catalogue")

    if request.method == "GET":
        return render(request, "kits/checkout.html", {"rows": rows, "total": total})

    name = request.POST.get("customer_name", "").strip()
    email = request.POST.get("email", "").strip()
    address = request.POST.get("delivery_address", "").strip()
    county = request.POST.get("county", "").strip()
    notes = request.POST.get("notes", "").strip()
    try:
        phone = _normalise_phone(request.POST.get("phone", ""))
    except ValueError as exc:
        messages.error(request, str(exc))
        return render(request, "kits/checkout.html", {"rows": rows, "total": total})

    if not name or not address:
        messages.error(request, "Enter your name and delivery address.")
        return render(request, "kits/checkout.html", {"rows": rows, "total": total})

    # Re-read product prices and stock inside the transaction; never accept a browser total.
    try:
        with transaction.atomic():
            locked_products = {}
            for row in rows:
                product = Product.objects.select_for_update().get(pk=row["product"].pk, active=True)
                if product.stock < row["quantity"]:
                    raise ValueError(f"Insufficient stock for {product.name}.")
                locked_products[product.pk] = product

            order = Order.objects.create(
                customer_name=name, email=email, phone=phone,
                delivery_address=address, county=county, notes=notes,
                total_amount=sum(locked_products[r["product"].pk].price * r["quantity"] for r in rows),
            )
            for row in rows:
                product = locked_products[row["product"].pk]
                OrderItem.objects.create(
                    order=order, product=product, product_name=product.name,
                    size=row["size"], quantity=row["quantity"],
                    unit_price=product.price, line_total=product.price * row["quantity"],
                )
            payment = MpesaPayment.objects.create(
                order=order, phone=phone, amount=order.total_amount,
                status=MpesaPayment.Status.INITIATED,
            )
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("kits:cart")

    try:
        result = stk_push(
            phone=phone,
            amount=order.total_amount,
            account_reference=order.public_reference,
            description="APS Bomet kits",
        )
        payment.merchant_request_id = result.get("MerchantRequestID", "")
        payment.checkout_request_id = result.get("CheckoutRequestID") or None
        payment.status = MpesaPayment.Status.PENDING
        payment.result_description = result.get("CustomerMessage", result.get("ResponseDescription", "STK request sent"))
        payment.save()
        if result.get("ResponseCode") != "0" or not payment.checkout_request_id:
            payment.status = MpesaPayment.Status.FAILED
            payment.result_description = result.get("ResponseDescription", "Daraja did not accept the STK request.")
            payment.save()
            order.status = Order.Status.FAILED
            order.save(update_fields=["status", "updated_at"])
            messages.error(request, payment.result_description)
            return redirect("kits:order_status", order_number=order.number)
    except Exception as exc:
        logger.exception(
        "MPESA STK PUSH ERROR for order %s",
        order.public_reference
        )
        
        payment.status = MpesaPayment.Status.FAILED
        payment.result_description = str(exc)[:500]
        payment.save()
        
        order.status = Order.Status.FAILED
        order.save(update_fields=["status", "updated_at"])
        
        messages.error(
        request,
        f"M-Pesa Error: {str(exc)}"
        )
        
        return redirect(
        "kits:order_status",
        order_number=order.number)
    
    request.session["aps_last_order"] = str(order.number)
    save_cart(request, {})
    return redirect("kits:order_status", order_number=order.number)


def order_status(request, order_number):
    order = get_object_or_404(
        Order,
        number=order_number
    )

    payment = order.payments.order_by(
        "-created_at"
    ).first()

    return render(
        request,
        "kits/order_status.html",
        {
            "order": order,
            "payment": payment
        }
    )

@require_GET
def order_status_json(request, order_number):

    order = get_object_or_404(
        Order,
        number=order_number
    )

    payment = order.payments.order_by(
        "-created_at"
    ).first()

    return JsonResponse({
        "order_status": order.status,

        "payment_status": (
            payment.status if payment else "unknown"
        ),

        "receipt": (
            payment.mpesa_receipt if payment else ""
        ),

        "message": (
            payment.result_description if payment else ""
        )
    })
    


@csrf_exempt
@require_POST
def mpesa_callback(request):
    try:
        body = json.loads(request.body.decode("utf-8"))
        callback = body["Body"]["stkCallback"]

        checkout_id = callback.get("CheckoutRequestID")
        result_code = int(callback.get("ResultCode", -1))

        if not checkout_id:
            logger.error("M-Pesa callback missing CheckoutRequestID")
            return JsonResponse({
                "ResultCode": 1,
                "ResultDesc": "Missing CheckoutRequestID"
            })

        with transaction.atomic():

            payment = MpesaPayment.objects.select_for_update().filter(
                checkout_request_id=checkout_id
            ).first()

            if payment is None:
                logger.error(
                    "No payment found for CheckoutRequestID: %s",
                    checkout_id
                )
                return JsonResponse({
                    "ResultCode": 0,
                    "ResultDesc": "Unknown checkout"
                })

            payment.raw_callback = body
            payment.result_code = str(result_code)
            payment.result_description = callback.get("ResultDesc", "")

            if result_code == 0:

                metadata = callback.get(
                    "CallbackMetadata", {}
                ).get("Item", [])

                values = {
                    item["Name"]: item.get("Value")
                    for item in metadata
                }

                receipt = str(
                    values.get("MpesaReceiptNumber", "")
                )

                paid_amount = int(float(
                    values.get("Amount", 0)
                ))

                paid_phone = str(
                    values.get("PhoneNumber", "")
                )

                # Verify payment against the saved order.
                if (
                    paid_amount != payment.amount
                    or paid_phone != payment.phone
                    or not receipt
                ):
                    payment.status = MpesaPayment.Status.FAILED

                    payment.result_description = (
                        "Payment details mismatch. "
                        "Manual verification required."
                    )

                    logger.error(
                        "Payment mismatch for %s",
                        checkout_id
                    )

                else:
                    payment.status = MpesaPayment.Status.SUCCESS
                    payment.mpesa_receipt = receipt

                    order = payment.order
                    order.status = Order.Status.PAID

                    # Deduct stock only once.
                    if not order.stock_deducted:

                        for item in order.items.select_related("product"):

                            Product.objects.filter(
                                pk=item.product_id
                            ).update(
                                stock=F("stock") - item.quantity
                            )

                        order.stock_deducted = True

                    order.save(update_fields=[
                        "status",
                        "stock_deducted",
                        "updated_at"
                    ])

                    logger.info(
                        "PAYMENT CONFIRMED: Order %s, Receipt %s",
                        order.public_reference,
                        receipt
                    )
                    #send_payment_confirmation(payment.id)

            else:
                payment.status = MpesaPayment.Status.FAILED

                if payment.order.status != Order.Status.PAID:
                    payment.order.status = Order.Status.FAILED
                    payment.order.save(update_fields=[
                        "status",
                        "updated_at"
                    ])

            payment.save()
            
        return JsonResponse({
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        })

    except Exception:
        logger.exception("MPESA CALLBACK PROCESSING ERROR")

        return JsonResponse({
            "ResultCode": 1,
            "ResultDesc": "Callback processing error"
        }, status=500)
