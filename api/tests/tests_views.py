from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Category, MenuItem, Cart, CartItem, Order, OrderItem
from django.contrib.auth.models import User, Group
from decimal import Decimal
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile


class CategoryViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.manager_group = Group.objects.create(name="Managers")
        self.user = User.objects.create_user(username="manager", password="pass")
        self.user.groups.add(self.manager_group)
        self.client.login(username="manager", password="pass")
        self.category_data = {"name": "Drinks"}

    def test_create_category(self):
        response = self.client.post(reverse("category-list"), self.category_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.get().name, "Drinks")

    def test_list_categories(self):
        Category.objects.create(name="Drinks")
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class MenuItemViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.manager_group = Group.objects.create(name="Managers")
        self.user = User.objects.create_user(username="manager", password="pass")
        self.user.groups.add(self.manager_group)
        self.client.login(username="manager", password="pass")
        self.category = Category.objects.create(name="Drinks")

        image = Image.new("RGB", (100, 100))
        image_file = BytesIO()
        image.save(image_file, "jpeg")
        image_file.seek(0)
        image = SimpleUploadedFile(
            "test_image.jpg", image_file.read(), content_type="image/jpeg"
        )

        self.menu_item_data = {
            "name": "Coke",
            "price": Decimal("1.99"),
            "category": self.category.id,
            "description": "A refreshing beverage",
            "image": image,
        }

    def test_create_menu_item(self):
        response = self.client.post(reverse("menuitem-list"), self.menu_item_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuItem.objects.count(), 1)
        self.assertEqual(MenuItem.objects.get().name, "Coke")

    def test_list_menu_items(self):
        MenuItem.objects.create(
            name="Coke",
            price=Decimal("1.99"),
            category=self.category,
            description="A refreshing beverage",
        )
        response = self.client.get(reverse("menuitem-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class CartViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="customer", password="pass")
        self.client.login(username="customer", password="pass")
        self.category = Category.objects.create(name="Drinks")
        self.menu_item = MenuItem.objects.create(
            name="Coke", price=Decimal("1.99"), category=self.category
        )

    def test_add_to_cart(self):
        response = self.client.post(
            reverse("cart-list"), {"menuitem": self.menu_item.id, "quantity": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.get().quantity, 2)

    def test_list_cart_items(self):
        cart = Cart.objects.create(customer=self.user)
        CartItem.objects.create(cart=cart, menuitem=self.menu_item, quantity=2)
        response = self.client.get(reverse("cart-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 1)


class OrderViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="customer", password="pass")
        self.client.login(username="customer", password="pass")
        self.category = Category.objects.create(name="Drinks")
        self.menu_item = MenuItem.objects.create(
            name="Coke", price=Decimal("1.99"), category=self.category
        )
        self.cart = Cart.objects.create(customer=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, menuitem=self.menu_item, quantity=2
        )

    def test_create_order(self):
        response = self.client.post(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_list_orders(self):
        order = Order.objects.create(customer=self.user)
        OrderItem.objects.create(order=order, menuitem=self.menu_item, quantity=2)
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
