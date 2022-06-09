from rest_framework import serializers

from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField

from apps.users.models import (
    User,
    EmployeeProfile,
    ShopBranch,
)
from apps.product.models import Product
from apps.order.models import Order


class ShopBranchSerializer(serializers.ModelSerializer):
    """Shop branch serializer"""

    class Meta:
        model = ShopBranch
        fields = '__all__'


class RegisterEmployeeSerializer(serializers.ModelSerializer):
    """Employee registration serializer"""

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "phone",
            "user_type",
            "shop_branch",
            "image",
            "is_active",
        ]
        read_only_fields = ['is_active']
        extra_kwargs = {
            "phone": {"required": True},
            "username": {"required": True},
            "password": {"write_only": True},
            "user_type": {"required": True},
            "shop_branch": {"required": False},
            "image": {"required": False},
        }

    def create(self, validated_data):
        user = User.objects.create(
            phone=validated_data["phone"],
            username=validated_data["username"],
            user_type=validated_data["user_type"],
            shop_branch=validated_data["shop_branch"],
            image=validated_data["image"],
        )
        user.set_password(validated_data["password"])
        user.save()

        return user


class RegisterClientSerializer(serializers.ModelSerializer):
    """Client registration serializer"""

    class Meta:
        model = User
        fields = [
            "username",
            "phone",
            "user_type",
            "image",
        ]
        extra_kwargs = {
            "phone": {"required": True},
            "username": {"required": True},
            "user_type": {"required": True},
            "image": {"required": False},
        }
        read_only_fields = ['user_type']


class LoginEmployeeSerializer(serializers.ModelSerializer):
    """Login employee serializer"""

    class Meta:
        model = User
        fields = ["phone", "password"]


class LoginClientSerializer(serializers.ModelSerializer):
    """Login client serializer"""

    class Meta:
        model = User
        fields = ["phone"]


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""

    shop_branch = PresentablePrimaryKeyRelatedField(
        queryset=ShopBranch.objects.all(),
        presentation_serializer=ShopBranchSerializer
    )

    class Meta:
        model = User
        fields = [
            "username",
            "phone",
            "user_type",
            "image",
            "is_active",
            "password",
            "shop_branch",
        ]


class EmployeeProfileSerializer(serializers.ModelSerializer):
    """Employee profile serializer"""

    user = UserSerializer()

    class Meta:
        model = EmployeeProfile
        fields = '__all__'

    def update(self, instance, validated_data):
        """Update nested UserSerializer fields """

        if 'user' in validated_data:
            nested_serializer = self.fields['user']
            nested_instance = instance.user
            nested_data = validated_data.pop('user')

            # Runs the update on whatever serializer the nested data belongs to
            nested_serializer.update(nested_instance, nested_data)

            # Runs the original parent update(), since the nested fields were
            # "popped" out of the data
        return super(EmployeeProfileSerializer, self).update(instance, validated_data)


class EmployeeProfileStatisticSerializer(EmployeeProfileSerializer):
    """Employee profile statistic serializer"""

    orders_quantity = serializers.SerializerMethodField('get_order_quantity')

    class Meta:
        model = EmployeeProfile
        fields = '__all__'

    @staticmethod
    def get_order_quantity(obj):
        if obj.user.user_type == 'florist':
            return Product.objects.filter(florist=obj.user.id, status='Продан').count()

        elif obj.user.user_type == 'courier':
            return Order.objects.filter(courier=obj.user.id, status='Доставлено').count()
