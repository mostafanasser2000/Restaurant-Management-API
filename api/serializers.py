from rest_framework import serializers
from .models import MenuItem, Category, Cart, CartItem, Order, OrderItem
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from django.contrib.auth.models import User
import bleach
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class UserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):
        fields = ["id", "username", "first_name", "last_name", "email", "password"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]
        extra_kwargs = {
            "slug": {"read_only": True},
        }

    def validate(self, attrs):
        attrs["name"] = bleach.clean(attrs["name"])
        return super().validate(attrs)


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(
        source="category", read_only=True, many=False
    )
    image = serializers.ImageField()

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "featured",
            "category",
            "category_name",
            "description",
            "image",
        ]
        extra_kwargs = {
            "slug": {"read_only": True},
        }

    def validate(self, attrs):
        if attrs["price"] < 0:
            raise serializers.ValidationError("Price cannot be negative")
        attrs["name"] = bleach.clean(attrs["name"])
        if "description" in attrs:
            attrs["description"] = bleach.clean(attrs["description"])
        return super().validate(attrs)


class CartItemSerializer(serializers.ModelSerializer):
    item_name = serializers.StringRelatedField(
        source="menuitem", read_only=True, many=False
    )

    class Meta:
        model = CartItem
        fields = ["id", "menuitem", "item_name", "quantity", "unit_price", "price"]
        extra_kwargs = {
            "quantity": {"min_value": 1},
            "unit_price": {"read_only": True},
            "price": {"read_only": True},
        }

    def validate(self, attrs):
        if attrs["quantity"] < 0:
            raise serializers.ValidationError("quantity cannot be negative")
        return super().validate(attrs)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["customer", "items"]


class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.StringRelatedField(
        source="menuitem", read_only=True, many=False
    )

    class Meta:
        model = OrderItem
        fields = ["id", "menuitem", "item_name", "quantity", "price", "total_cost"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "created",
            "updated",
            "paid",
            "status",
            "discount",
            "subtotal",
            "total",
            "items",
        ]

        extra_kwargs = {
            "paid": {"read_only": True},
            "created": {"read_only": True},
            "updated": {"read_only": True},
            "discount": {"read_only": True},
            "subtotal": {"read_only": True},
            "total": {"read_only": True},
            "status": {"read_only": True},
        }


class CustomOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = UserSerializer(read_only=True)
    delivery_crew = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "delivery_crew",
            "created",
            "updated",
            "paid",
            "status",
            "discount",
            "subtotal",
            "total",
            "items",
        ]

        extra_kwargs = {
            "paid": {"read_only": True},
            "created": {"read_only": True},
            "updated": {"read_only": True},
            "discount": {"read_only": True},
            "subtotal": {"read_only": True},
            "total": {"read_only": True},
            "status": {"read_only": True},
        }
