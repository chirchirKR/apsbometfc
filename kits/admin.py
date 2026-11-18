from django.contrib import admin
from .models import Product, ProductImage, Order, OrderItem, MpesaPayment


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "active", "updated_at")
    list_filter = ("active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "product_name", "size", "quantity", "unit_price", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("public_reference", "customer_name", "phone", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "phone", "email", "number")
    readonly_fields = ("number", "total_amount", "stock_deducted", "created_at", "updated_at")
    inlines = [OrderItemInline]


@admin.register(MpesaPayment)
class MpesaPaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "phone", "amount", "status", "mpesa_receipt", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("phone", "checkout_request_id", "mpesa_receipt")
    readonly_fields = ("raw_callback", "created_at", "updated_at")
