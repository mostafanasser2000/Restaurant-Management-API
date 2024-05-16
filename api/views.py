from django.shortcuts import render
from rest_framework.response import Response
from .models import MenuItem, Cart, CartItem, Order, OrderItem, Category
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    CartItemSerializer,
    CartSerializer,
    OrderItemSerializer,
    OrderSerializer,
)
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def add_to_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        item_id = request.data.get("menuitem")
        quantity = request.data.get("quantity", 1)
        menuitem = get_object_or_404(MenuItem, pk=item_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, menuitem=menuitem
        )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

    def remove_from_cart(self, request, pk=None):
        cart_item = get_object_or_404(CartItem, cart__user=request.user, pk=pk)
        cart_item.delete()
        return Response(
            {"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT
        )


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        if cart.items.count() == 0:
            return Response(
                {"message": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )
        order = Order.objects.create(user=request.user)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order, menuitem=item.menuitem, quantity=item.quantity
            )
        cart.items.all().delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
