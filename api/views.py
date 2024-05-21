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
    UserSerializer,
    CustomOrderSerializer,
)
from rest_framework import viewsets, status, filters
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
)
from django.shortcuts import get_object_or_404
from .permissions import IsManager, IsDeliveryCrew
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManager]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManager]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "featured"]
    search_fields = ["title"]
    ordering_fields = ["price"]


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        List all cart items
        """
        cart, created = Cart.objects.get_or_create(customer=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Get an item from cart
        """
        cart_item = get_object_or_404(CartItem, cart__customer=self.request.user, pk=pk)
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    def add_to_cart(self, request):
        """
        Add an item to cart
        """
        cart, created = Cart.objects.get_or_create(customer=request.user)

        item_id = request.data.get("menuitem")
        quantity = int(request.data.get("quantity", 1))
        menuitem = get_object_or_404(MenuItem, pk=item_id)

        if quantity < 0:
            return Response(
                {"detail": "quantity cannot be negative", "status": "fail"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, menuitem=menuitem
        )

        if not created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        # Serialize the cart item after it's saved
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from_cart(self, request, pk=None):
        """
        Remove an item from cart
        """
        cart_item = get_object_or_404(CartItem, cart__customer=request.user, pk=pk)
        cart_item.delete()
        return Response(
            {"detail": "Item removed from cart", "status": "ok"},
            status=status.HTTP_204_NO_CONTENT,
        )


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_fields = ["paid", "status"]
    ordering_fields = ["created", "total"]

    def get_serializer_class(self):
        user = self.request.user
        if (
            user.is_superuser
            or user.groups.filter(name__in=["Managers", "Crew"]).exists()
        ):
            return CustomOrderSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action in ["list", "update", "partial_update"]:
            permission_classes = [IsAuthenticated]
            if (
                self.request.user.groups.filter(name="Managers").exists()
                or self.request.user.is_superuser
            ):
                permission_classes.append(IsManager)
            elif self.request.user.groups.filter(name="Crew").exists():
                permission_classes.append(IsDeliveryCrew)

        return [permission() for permission in self.permission_classes]

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name="Managers").exists() or user.is_superuser:
            queryset = Order.objects.all()
        elif user.groups.filter(name="Crew").exists():
            queryset = Order.objects.filter(delivery_crew=user)
        else:
            queryset = Order.objects.filter(customer=user)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user
        if (
            user.groups.filter(name="Managers").exists()
            or user.is_superuser
            or order.customer == user
            or order.delivery_crew == user
        ):
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        return Response(
            {"detail": "Not authorized to view this order"},
            status=status.HTTP_403_FORBIDDEN,
        )

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(Q(name="Managers") | Q(name="Crew")):
            return Response(
                {"only customers can make orders"}, status=status.HTTP_403_FORBIDDEN
            )

        cart = Cart.objects.get(customer=user)
        if cart.items.count() == 0:
            return Response(
                {"detail": "Cart is empty", "status": "fail"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order = Order.objects.create(customer=user)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order, menuitem=item.menuitem, quantity=item.quantity
            )
        cart.items.all().delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name="Managers").exists() or user.is_superuser:
            return super().update(request, *args, **kwargs)
        return Response(
            {"detail": "Not authorized to update this order."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        order = self.get_object()
        if (
            user.groups.filter(name="Managers").exists()
            or user.is_superuser
            or user.groups.filter(name="Crew").exists()
        ):
            if "status" in request.data:
                order.status = request.data["status"]
                order.save()
                return Response(
                    {"order_status": order.status}, status=status.HTTP_200_OK
                )

            if "delivery_crew" in request.data and (
                user.groups.filter(name="Managers").exists() or user.is_superuser
            ):
                order.delivery_crew = get_object_or_404(
                    User, pk=request.data["delivery_crew"]
                )
                order.save()
                serializer = UserSerializer(order.delivery_crew)
                return Response(
                    {"delivery_crew": serializer.data}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "detail": "Only the status and delivery_crew fields can be updated."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {"detail": "Not authorized to update this order."},
            status=status.HTTP_403_FORBIDDEN,
        )


class ManagerViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(groups__name="Managers")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = get_object_or_404(User, email=request.data.get("email"))
        manager_group, created = Group.objects.get_or_create(name="Managers")
        if manager_group.user_set.filter(id=user.id).exists():
            return Response(
                {"detail": "User already exists in Managers group."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        manager_group.user_set.add(user)
        return Response(
            {"detail": "User is added to Managers group.", "status": "ok"},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        manager_group = Group.objects.get(name="Managers")
        if not manager_group.user_set.filter(id=user.id).exists():
            return Response(
                {"detail": "User is not in Managers group.", "status": "fail"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        manager_group.user_set.remove(user)
        return Response(
            {"detail": "User is removed from Managers group.", "status": "ok"},
            status=status.HTTP_204_NO_CONTENT,
        )


class DeliveryCrewViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(groups__name="Crew")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = get_object_or_404(User, email=request.data.get("email"))
        crew_group, created = Group.objects.get_or_create(name="Crew")
        if crew_group.user_set.filter(id=user.id).exists():
            return Response(
                {"detail": "User already exists in Delivery Crew group."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        crew_group.user_set.add(user)
        return Response(
            {"detail": "User is added to Delivery Crew group.", "status": "ok"},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        crew_group = Group.objects.get(name="Crew")
        if not crew_group.user_set.filter(id=user.id).exists():
            return Response(
                {"detail": "User is not in Delivery Crew group.", "status": "fail"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        crew_group.user_set.remove(user)
        return Response(
            {"detail": "User is removed from Delivery Crew group.", "status": "ok"},
            status=status.HTTP_204_NO_CONTENT,
        )
