from django.db import models
from django.utils import timezone

from apps.users.models import User, EmployeeProfile


class Product(models.Model):
    """Product model"""

    product_status = [
        ('На продаже', 'На продаже'),
        ('Продан', 'Продан'),
        ('В процессе доставки', 'В процессе доставки'),
        ('Удален', 'Удален')
    ]

    size_choice = [
        ('Маленький', 'Маленький'),
        ('Средний', 'Средний'),
        ('Большой', 'Большой'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    product_type = models.ForeignKey('ProductType', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=9, decimal_places=1, default=0)
    price_without_allowance = models.DecimalField(max_digits=9, decimal_places=1, default=0)
    size = models.CharField(max_length=255, choices=size_choice)
    creation_date = models.DateTimeField(auto_now_add=True)
    florist = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.CharField(max_length=255, choices=product_status, default='На продаже')
    sale_datetime = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        product_type = self.product_type
        if product_type.title == 'Комнатное':
            total_allowance = product_type.florist_allowance + product_type.courier_allowance + product_type.allowance
            self.price = self.price_without_allowance + self.price_without_allowance / 100 * total_allowance
        super().save(*args, **kwargs)

    @property
    def florist_percent(self):
        return self.price_without_allowance / 100 * self.product_type.florist_allowance

    @property
    def shop_branch(self):
        return self.florist.shop_branch.address

    @property
    def freshness_status(self):
        current_datetime = timezone.now()
        time_difference = current_datetime - self.creation_date
        day = time_difference.total_seconds() // 86400
        month = day // 31

        if self.product_type.title == 'Букет' and day <= 3:
            return "Цветущий"
        elif self.product_type.title == 'Букет' and day > 3:
            return "Увядший"
        if self.product_type.title == 'Комнатное' and month <= 6:
            return "Цветущий"
        elif self.product_type.title == 'Комнатное' and month > 6:
            return "Увядший"


class ProductType(models.Model):
    """Product type model"""

    title = models.CharField(max_length=255)
    allowance = models.PositiveIntegerField(null=True)
    florist_allowance = models.PositiveIntegerField(null=True)
    courier_allowance = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f'{self.title}'


class ProductImage(models.Model):
    """Product image model"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f'{self.product}'


class Flower(models.Model):
    """Flower model"""

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=9, decimal_places=1, default=0)
    total_quantity = models.PositiveIntegerField()
    image = models.ImageField(null=True)

    def __str__(self):
        return f'{self.name}'


class ProductFlower(models.Model):
    """Product Flower model"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, limit_choices_to={'status': 'На продаже'})
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=9, decimal_places=1, default=0)

    def __str__(self):
        return f'{self.product}'

    def save(self, *args, **kwargs):
        self.price = self.flower.price * self.quantity
        super().save(*args, **kwargs)


class FavoriteProduct(models.Model):
    """User favorite product model"""

    client = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.product} {self.client}'
