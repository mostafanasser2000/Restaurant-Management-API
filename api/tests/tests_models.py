from django.test import TestCase
from django.contrib.auth.models import User
from api.models import Category, MenuItem, Cart, CartItem, Order, OrderItem
from decimal import Decimal


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Drinks")

    def test_create_category(self):
        self.assertEqual(self.category.name, "Drinks")
        self.assertEqual(self.category.slug, "drinks")
        self.assertTrue(isinstance(self.category, Category))
        self.assertEqual(str(self.category), self.category.name)


class MenuItemModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Drinks")
        self.menu_item = MenuItem.objects.create(
            name="Coke",
            price=Decimal("1.99"),
            category=self.category,
            description="A refreshing beverage",
        )

    def test_create_menu_item(self):
        self.assertEqual(self.menu_item.name, "Coke")
        self.assertEqual(self.menu_item.slug, "coke")
        self.assertEqual(self.menu_item.price, Decimal("1.99"))
        self.assertEqual(self.menu_item.category, self.category)
        self.assertTrue(isinstance(self.menu_item, MenuItem))
        self.assertEqual(str(self.menu_item), self.menu_item.name)


class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.cart = Cart.objects.create(customer=self.user)
        self.category = Category.objects.create(name="Drinks")
        self.menu_item = MenuItem.objects.create(
            name="Coke", price=Decimal("1.99"), category=self.category
        )
        self.cart_item = CartItem.objects.create(
            cart=self.cart, menuitem=self.menu_item, quantity=2
        )

    def test_create_cart_item(self):
        self.assertEqual(self.cart_item.cart, self.cart)
        self.assertEqual(self.cart_item.menuitem, self.menu_item)
        self.assertEqual(self.cart_item.unit_price, self.menu_item.price)
        self.assertEqual(self.cart_item.price, self.menu_item.price * 2)
        self.assertTrue(isinstance(self.cart_item, CartItem))
        self.assertEqual(str(self.cart_item), self.menu_item.name)


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.order = Order.objects.create(customer=self.user)

    def test_create_order(self):
        self.assertEqual(self.order.customer, self.user)
        self.assertEqual(self.order.status, "pending")
        self.assertTrue(isinstance(self.order, Order))
        self.assertEqual(str(self.order), f"Order {self.order.id}")


class OrderItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpass")
        self.order = Order.objects.create(customer=self.user)
        self.category = Category.objects.create(name="Drinks")
        self.menu_item = MenuItem.objects.create(
            name="Coke", price=Decimal("1.99"), category=self.category
        )
        self.order_item = OrderItem.objects.create(
            order=self.order, menuitem=self.menu_item, quantity=2
        )

    def test_create_order_item(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.menuitem, self.menu_item)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, self.menu_item.price)
        self.assertTrue(isinstance(self.order_item, OrderItem))
        self.assertEqual(str(self.order_item), str(self.order_item.id))
        self.assertEqual(self.order_item.total_cost, self.order_item.price * 2)
