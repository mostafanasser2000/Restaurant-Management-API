from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MenuItemViewSet,
    CartViewSet,
    OrderViewSet,
    CategoryViewSet,
    ManagerViewSet,
    DeliveryCrewViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"menu-items", MenuItemViewSet, basename="menuitem")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"managers", ManagerViewSet, basename="manager")
router.register(r"delivery_crew", DeliveryCrewViewSet, basename="delivery-crew")

cart_list = CartViewSet.as_view({"get": "list", "post": "add_to_cart"})
cart_remove = CartViewSet.as_view({"delete": "remove_from_cart"})

urlpatterns = [
    path("", include(router.urls)),
    path("cart/", cart_list, name="cart-list"),
    path("cart/<int:pk>/", cart_remove, name="cart-remove"),
]
