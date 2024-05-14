from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    featured = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="menu_items"
    )
    description = models.CharField(max_length=255, blank=True)
    # image = models.ImageField(upload_to="media/", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["-created"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Cart"


class CartItem(models.Model):
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    class Meta:
        unique_together = ("cart", "menuitem")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.unit_price = self.item.price
        self.price = self.unit_price * self.quantity

    def __str__(self):
        return self.item.title


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    # first_name = models.CharField(max_length=50, blank=True)
    # last_name = models.CharField(max_length=50, blank=True)
    # email = models.EmailField(blank=True)
    # address = models.CharField(max_length=255)
    # postal_code = models.CharField(max_length=20)
    # city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0
    )

    class Meta:
        ordering = ["-created"]
        indexes = [models.Index(fields=["-created"])]

    @property
    def subtotal(self):
        return self.total - self.get_discount()

    @property
    def total(self):
        return sum(item.total_cost for item in self.items.all())

    def get_discount(self):
        if self.discount:
            return self.total * (self.discount / Decimal(100))
        return Decimal(0)

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menuitem = models.ForeignKey(
        MenuItem, related_name="order_items", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.id)

    @property
    def total_cost(self):
        return self.price * self.quantity
