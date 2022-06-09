from rest_framework import serializers

from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField

from apps.users.serializers import UserSerializer
from apps.users.models import EmployeeProfile, User
from apps.product.models import (
    Product,
    Flower,
    ProductFlower,
    ProductType,
    ProductImage,
    FavoriteProduct,
)


class ProductTypeSerializer(serializers.ModelSerializer):
    """Product type serializer"""

    class Meta:
        model = ProductType
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer"""

    florist = PresentablePrimaryKeyRelatedField(
        queryset=User.objects.all(),
        presentation_serializer=UserSerializer
    )
    product_type = PresentablePrimaryKeyRelatedField(
        queryset=ProductType.objects.all(),
        presentation_serializer=ProductTypeSerializer
    )
    creation_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    sale_datetime = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    florist_percent = serializers.DecimalField(max_digits=9, decimal_places=1, read_only=True)
    courier_percent = serializers.DecimalField(max_digits=9, decimal_places=1, read_only=True)
    freshness_status = serializers.ReadOnlyField()
    shop_branch = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = [
            'is_ordered',
            'is_sold',
            'shop_branch',
            'status',
            'price',
        ]


class ProductAdminSerializer(ProductSerializer):
    """Product serializer for Admins"""

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = [
            'is_ordered',
            'is_sold',
            'shop_branch',
            'price',
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    """Product Image serializer"""

    product = PresentablePrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        presentation_serializer=ProductSerializer
    )

    class Meta:
        model = ProductImage
        fields = '__all__'


class FlowerSerializer(serializers.ModelSerializer):
    """Flower serializer"""

    class Meta:
        model = Flower
        fields = '__all__'


class ProductFlowerSerializer(serializers.ModelSerializer):
    """Product-flower serializer"""
    product = PresentablePrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        presentation_serializer=ProductSerializer
    )
    flower = PresentablePrimaryKeyRelatedField(
        queryset=Flower.objects.all(),
        presentation_serializer=FlowerSerializer
    )

    class Meta:
        model = ProductFlower
        fields = '__all__'
        read_only_fields = ['price']


class FavoriteProductSerializer(serializers.ModelSerializer):
    """Favorite product serializer"""

    product = PresentablePrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        presentation_serializer=ProductSerializer
    )

    class Meta:
        model = FavoriteProduct
        fields = '__all__'
        read_only_fields = ['client']


class FloristHistorySerializer(serializers.Serializer):
    """Florist product history serializer"""

    products = ProductSerializer(many=True)
    total_earnings = serializers.SerializerMethodField('get_total_earnings')

    @staticmethod
    def get_total_earnings(obj):
        return sum([obj['products'].florist_percent for obj['products'] in obj['products'].all()])
