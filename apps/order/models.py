from django.db import models

from apps.users.models import User
from apps.product.models import (
    Product,
    ProductFlower,
    ProductType
)


class Cart(models.Model):
    """Cart model"""

    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_ordered = models.BooleanField(default=False)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.client}'

    @property
    def total_price(self):
        cart_product = CartProduct.objects.filter(cart=self.pk)
        total_price = 0
        for a in cart_product:
            total_price += a.price
        return total_price


class CartProduct(models.Model):
    """CartProduct model"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, limit_choices_to={'status': 'На продаже'})
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, limit_choices_to={'is_ordered': False})
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=9, decimal_places=1)

    def __str__(self):
        return f'{self.product}'

    def save(self, *args, **kwargs):
        self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)


class Order(models.Model):
    """Order model"""

    order_status_choices = [
        ('На рассмотрении', 'На рассмотрении'),
        ('В ожидании курьера', 'В ожидании курьера'),
        ('Курьер принял заказ', 'Курьер принял заказ'),
        ('Курьер едет к нам', 'Курьер едет к нам'),
        ('Заказ у курьера', 'Заказ у курьера'),
        ('Ваш заказ в пути', 'Ваш заказ в пути'),
        ('Доставлено', 'Доставлено'),
        ('Отменен', 'Отменен'),

    ]

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, limit_choices_to={'is_ordered': False})
    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='order_client')
    sender_name = models.CharField(max_length=255, null=True)
    sender_phone_number = models.CharField(max_length=255, null=True)
    receiver_name = models.CharField(max_length=255, null=True)
    receiver_phone_number = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255)
    postcard_text = models.TextField(null=True)
    total_price = models.DecimalField(max_digits=9, decimal_places=1)
    money_change_status = models.BooleanField(default=False)
    client_money_value = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    received_date = models.DateField()
    received_time = models.TimeField()
    courier = models.ForeignKey(User, on_delete=models.PROTECT, related_name='order_courier', null=True)
    status = models.CharField(max_length=255, choices=order_status_choices)

    def __str__(self):
        return f'{self.client}'

    def save(self, *args, **kwargs):
        self.total_price = self.cart.total_price
        super().save(*args, **kwargs)

    @property
    def money_change_value(self):
        if self.money_change_status is True:
            return self.client_money_value - self.total_price

    @property
    def products(self):
        cart_product = CartProduct.objects.filter(cart=self.cart)
        return cart_product.values(
            'product__id',
            'product__name',
            'product__product_type__title',
            'product__product_type__courier_allowance',
            'product__price',
            'product__price_without_allowance',
        )

    @property
    def courier_percent(self):
        products = [products for products in self.products]
        product_price = [key['product__price_without_allowance'] for key in products]
        courier_allowance = [key['product__product_type__courier_allowance'] for key in products]
        for courier_allowances in courier_allowance:
            price = [product_prices for product_prices in product_price]
            courier_percent = sum(price) / 100 * courier_allowances
            return courier_percent
