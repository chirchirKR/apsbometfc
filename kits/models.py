import uuid
from django.db import models
from django.utils.text import slugify


class Product(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField(help_text="Price in whole Kenyan shillings (KES).")
    stock = models.PositiveIntegerField(default=0)
    sizes = models.CharField(
        max_length=100, default="S,M,L,XL,XXL,3XL",
        help_text="Comma-separated sizes, e.g. S,M,L,XL,XXL,3XL"
    )
    main_image = models.ImageField(upload_to="kits/products/")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "kit"
            candidate = base
            n = 2
            while Product.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{n}"
                n += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def size_list(self):
        return [s.strip() for s in self.sizes.split(",") if s.strip()]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="kits/gallery/")
    alt_text = models.CharField(max_length=160, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"Image for {self.product.name}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Awaiting payment"
        PAID = "paid", "Paid"
        FAILED = "failed", "Payment failed"
        CANCELLED = "cancelled", "Cancelled"

    number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer_name = models.CharField(max_length=160)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15)
    delivery_address = models.TextField()
    county = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    total_amount = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    stock_deducted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"APS-{str(self.number)[:8].upper()} — {self.customer_name}"

    @property
    def public_reference(self):
        return f"APS-{str(self.number)[:8].upper()}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=160)
    size = models.CharField(max_length=12)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.PositiveIntegerField()
    line_total = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product_name} ({self.size}) x {self.quantity}"


class MpesaPayment(models.Model):
    class Status(models.TextChoices):
        INITIATED = "initiated", "STK request sent"
        PENDING = "pending", "Awaiting customer"
        SUCCESS = "success", "Successful"
        FAILED = "failed", "Failed"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    phone = models.CharField(max_length=15)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, unique=True, null=True)
    mpesa_receipt = models.CharField(max_length=40, blank=True, unique=True, null=True)
    result_code = models.CharField(max_length=20, blank=True)
    result_description = models.TextField(blank=True)
    raw_callback = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.public_reference} — {self.status}"
