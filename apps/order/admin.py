from django.contrib import admin

from apps.order.models import (
    Cart,
    CartProduct,
    Order,
)

admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Order)
