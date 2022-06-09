from django.contrib import admin

from apps.product.models import (
    Product,
    ProductType,
    ProductImage,
    Flower,
    ProductFlower,
    FavoriteProduct,
)


admin.site.register(Product)
admin.site.register(ProductType)
admin.site.register(ProductImage)
admin.site.register(Flower)
admin.site.register(ProductFlower)
admin.site.register(FavoriteProduct)

