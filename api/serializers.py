from rest_framework import serializers
from .models import MenuItem, Category, Cart, CartItem, Order, OrderItem
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from django.contrib.auth.models import User
import bleach


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]
        extra_kwargs = {
            "slug": "read_only",
        }

    def validate(self, attrs):
        attrs["name"] = bleach.clean(attrs["name"])
        return super().validate(attrs)


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.SlugRelatedField(
        source="category", read_only=True, many=False
    )

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
        ]
        extra_kwargs = {
            "slug": "read_only",
        }

    def validate(self, attrs):
        if attrs["price"] < 0:
            raise serializers.ValidationError("Price cannot be negative")
        attrs["name"] = bleach.clean(attrs["name"])
        attrs["description"] = bleach.clean(attrs["description"])
        return super().validate(attrs)


class CartItemSerializer(serializers.ModelSerializer):
    item_name = serializers.SlugRelatedField(
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


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["user", "items"]


class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.SlugRelatedField(
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
            "user",
            "created",
            "paid",
            "discount",
            "subtotal",
            "total",
            "items",
        ]
