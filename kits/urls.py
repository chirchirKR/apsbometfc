from django.urls import path
from . import views

app_name = "kits"

urlpatterns = [
    path("", views.catalogue, name="catalogue"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<str:key>/", views.update_cart, name="update_cart"),
    path("cart/remove/<str:key>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/<uuid:order_number>/", views.order_status, name="order_status"),
    path("order/<uuid:order_number>/status.json", views.order_status_json, name="order_status_json"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
]
