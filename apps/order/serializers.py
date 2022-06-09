from rest_framework import serializers

from apps.order.models import (
    Cart,
    CartProduct,
    Order,
)


class CartSerializer(serializers.ModelSerializer):
    """Cart serializer"""

    total_price = serializers.ReadOnlyField()
    creation_datetime = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = [
            'client',
            'is_ordered',
        ]


class CartProductSerializer(serializers.ModelSerializer):
    """CartProduct Serializer"""

    class Meta:
        model = CartProduct
        fields = '__all__'
        read_only_fields = [
            'price',
            'quantity',
        ]


class ClientOrderSerializer(serializers.ModelSerializer):
    """Order Serializer"""

    money_change_value = serializers.ReadOnlyField()
    products = serializers.ReadOnlyField()
    client = serializers.StringRelatedField()
    courier = serializers.StringRelatedField()
    creation_datetime = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = [
            'client',
            'courier',
            'status',
            'total_price',
        ]


class AdminOrderSerializer(ClientOrderSerializer):
    """Order Serializer"""

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = [
            'courier',
            'client',
        ]


class CourierOrderSerializer(AdminOrderSerializer):
    """Order Serializer"""

    courier_percent = serializers.DecimalField(max_digits=9, decimal_places=1, read_only=True)

    def __init__(self, *args, **kwargs):
        super(CourierOrderSerializer, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'status':
                self.fields[field].read_only = True

    class Meta:
        model = Order
        fields = '__all__'


class CourierHistorySerializer(serializers.Serializer):
    """Courier order history serializer"""

    order = CourierOrderSerializer(many=True)
    total_earnings = serializers.SerializerMethodField('get_total_earnings')

    @staticmethod
    def get_total_earnings(obj):
        return sum([obj['order'].courier_percent for obj['order'] in obj['order'].all()])
