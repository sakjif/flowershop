import datetime
import decimal

from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncWeek

from apps.order.models import Order
from apps.order.serializers import CourierHistorySerializer
from apps.product.models import (
    Product,
    ProductType,
    Flower,
    ProductFlower,
    ProductImage,
    FavoriteProduct,
)
from apps.product.serializers import (
    ProductSerializer,
    ProductAdminSerializer,
    ProductTypeSerializer,
    FlowerSerializer,
    ProductFlowerSerializer,
    ProductImageSerializer,
    FavoriteProductSerializer,
    FloristHistorySerializer,
)
from apps.users.permissions import (
    IsClient,
    IsFlorist,
    IsAdmin,
    IsFloristOrReadOnly,
    IsFloristOrAdminOnlyUpdateOrReadOnly,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


class ProductTypeView(ModelViewSet):
    """Product type View"""

    serializer_class = ProductTypeSerializer
    queryset = ProductType.objects.all()
    permission_classes = (IsAdmin,)


class ProductView(ModelViewSet):
    """Product View"""

    def get_serializer_class(self):
        """Filter serializer by user type"""

        user = self.request.user
        if user.is_anonymous or user.user_type == 'florist' or user.user_type == 'client':
            return ProductSerializer
        elif user.user_type == 'admin':
            return ProductAdminSerializer

    serializer_class = get_serializer_class
    queryset = Product.objects.all().order_by('-id')
    permission_classes = (IsFloristOrAdminOnlyUpdateOrReadOnly, )
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['status', 'product_type__title']

    def get_queryset(self):
        """Filter queryset by user type"""

        user = self.request.user
        if user.is_anonymous or user.user_type == 'client' or user.user_type == 'courier':
            return self.queryset.filter(status='На продаже')
        elif user.user_type == 'admin':
            return self.queryset
        elif user.user_type == 'florist':
            return self.queryset.filter(florist=user)

    def perform_create(self, serializer):
        serializer.save(florist=self.request.user)

    def perform_update(self, serializer):
        serializer.save(florist=self.request.user)


class FlowerView(ModelViewSet):
    """Flower View"""

    serializer_class = FlowerSerializer
    queryset = Flower.objects.all()
    permission_classes = (IsAdmin,)


class ProductFlowerView(ModelViewSet):
    """Product-flower View"""

    serializer_class = ProductFlowerSerializer
    queryset = ProductFlower.objects.filter(product__status='На продаже')
    permission_classes = (IsFlorist,)

    def get_queryset(self):
        """Filter product-flower by current florist"""

        queryset = self.queryset.filter(product__florist=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create product-flower with auto product price calculation
        and count flower quantity
        """

        serializer = ProductFlowerSerializer(data=request.data)
        if serializer.is_valid():
            flower = serializer.validated_data['flower']
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            if product.florist == self.request.user:
                flower.total_quantity -= quantity
                flower.save()
                serializer.save()
                allowance = product.product_type.allowance
                florist_allowance = product.product_type.florist_allowance
                courier_allowance = product.product_type.courier_allowance
                total_allowance = florist_allowance + courier_allowance + allowance
                product.price_without_allowance += decimal.Decimal(serializer.data['price'])
                product.price += decimal.Decimal(serializer.data['price']) \
                                 + (decimal.Decimal(serializer.data['price']) / 100 * total_allowance)
                product.save()
                return Response(serializer.data)

            elif product.florist != self.request.user:
                return Response({'Этот продукт принадлежит другому флористу'}, status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """
        Delete product-flower with auto product price calculation
        and count flower quantity
        """

        instance = self.get_object()
        instance.flower.total_quantity += instance.quantity
        instance.flower.save()
        product_type = instance.product.product_type
        total_allowance = product_type.florist_allowance + product_type.courier_allowance + product_type.allowance
        instance.product.price -= instance.price + (instance.price / 100 * total_allowance)
        instance.product.price_without_allowance -= instance.price
        instance.product.save()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImageView(ModelViewSet):
    """Product Image View"""

    serializer_class = ProductImageSerializer
    queryset = ProductImage.objects.all()
    permission_classes = (IsFloristOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['product__id']


class FavoriteProductView(ModelViewSet):
    """Favorite product view"""

    serializer_class = FavoriteProductSerializer
    queryset = FavoriteProduct.objects.all()
    permission_classes = (IsClient,)

    def get_queryset(self):
        """Filter favorite products by current client"""

        queryset = self.queryset.filter(client=self.request.user)
        return queryset

    def perform_create(self, serializer):
        """Add favorite product with current client"""

        serializer.save(client=self.request.user)


class NewProductView(ListAPIView):
    """New product view"""

    serializer_class = ProductSerializer
    queryset = Product.objects.order_by('-creation_date')[:10]
    permission_classes = (IsClient,)


class EmployeeHistoryView(APIView):
    """Employee history view"""

    def get(self, request):
        user = self.request.user
        if user.user_type == 'florist':
            products = Product.objects.filter(florist=user, status='Продан')
            serializer = FloristHistorySerializer({'products': products})
            return Response(serializer.data)
        elif user.user_type == 'courier':
            order = Order.objects.filter(courier=user, status='Доставлено')
            serializer = CourierHistorySerializer({'order': order})
            return Response(serializer.data)


class RevenueStatisticView(ListAPIView):
    """Revenue statistic view"""

    def list(self, request, *args, **kwargs):
        month = self.request.query_params.get('month')
        three_month = self.request.query_params.get('three_month')
        half_year = self.request.query_params.get('half_year')
        if month:
            duration = datetime.datetime.today() - datetime.timedelta(days=30)
            queryset = Product.objects.filter(sale_datetime__gte=duration, status='Продан')\
                .annotate(week=TruncWeek("sale_datetime")).values("week").annotate(total_revenue=Sum("price"))
            return Response(queryset)

        if three_month:
            duration = datetime.date.today() - datetime.timedelta(days=90)
            queryset = Product.objects.filter(sale_datetime__gte=duration, status='Продан')\
                .annotate(week=TruncWeek("sale_datetime")).values("week").annotate(total_revenue=Sum("price"))
            return Response(queryset)

        if half_year:
            duration = datetime.date.today() - datetime.timedelta(days=182)
            queryset = Product.objects.filter(sale_datetime__gte=duration, status='Продан')\
                .annotate(week=TruncMonth("sale_datetime")).values("week").annotate(total_revenue=Sum("price"))
            return Response(queryset)
        return Response('Статистика выручки магазина')
