from decimal import Decimal
from .models import Product


CART_SESSION_KEY = "aps_kits_cart"


def get_cart(request):
    return request.session.get(CART_SESSION_KEY, {})


def save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def cart_details(request):
    cart = get_cart(request)
    rows = []
    total = 0
    cleaned = {}
    for key, data in cart.items():
        try:
            product = Product.objects.get(pk=int(data["product_id"]), active=True)
            qty = max(1, min(int(data["quantity"]), 20))
            size = str(data["size"]).strip()
            if size not in product.size_list:
                continue
            line_total = product.price * qty
            rows.append({"product": product, "size": size, "quantity": qty,
                         "unit_price": product.price, "line_total": line_total, "key": key})
            total += line_total
            cleaned[key] = {"product_id": product.pk, "size": size, "quantity": qty}
        except (Product.DoesNotExist, KeyError, ValueError, TypeError):
            continue
    if cleaned != cart:
        save_cart(request, cleaned)
    return rows, total
