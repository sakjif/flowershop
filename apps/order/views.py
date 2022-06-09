import datetime
from django.db.models import Count

from django.db.models.functions import TruncMonth, TruncWeek
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework import mixins, status

from apps.users.permissions import (
    IsClient,
    IsCourier,
    IsAdmin,
    IsOrderClient,
)
from apps.users.models import EmployeeProfile
from apps.order.models import (
    Cart,
    CartProduct,
    Order,
)
from apps.order.serializers import (
    CartSerializer,
    CartProductSerializer,
    ClientOrderSerializer,
    AdminOrderSerializer,
    CourierOrderSerializer,
)


class CartView(ModelViewSet):
    """Cart view"""

    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    permission_classes = (IsClient,)

    def get_queryset(self):
        """Filter cart by current client"""
        user = self.request.user

        if user.is_anonymous:
            return self.queryset.filter(id=-1)
        else:
            return self.queryset.filter(client=self.request.user, is_ordered=False)

    def perform_create(self, serializer):
        """Create cart by current client"""
        if self.request.user.is_authenticated:
            serializer.save(client=self.request.user)
        serializer.save()


class CartProductView(ModelViewSet):
    """CartProduct View"""

    serializer_class = CartProductSerializer
    queryset = CartProduct.objects.all()
    permission_classes = (IsClient,)

    def get_queryset(self):
        """Filter objects by active client cart """
        user = self.request.user

        if user.is_anonymous:
            return self.queryset.filter(id=-1)
        else:
            return self.queryset.filter(cart__is_ordered=False, cart__client=self.request.user)


class ClientOrderView(ModelViewSet):
    """Client order View"""

    serializer_class = ClientOrderSerializer
    queryset = Order.objects.all()
    permission_classes = (IsOrderClient,)

    def get_queryset(self):
        """Filter order by current client"""
        user = self.request.user

        if user.is_anonymous:
            return self.queryset.filter(id=-1)
        else:
            return self.queryset.filter(client=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            cart = serializer.validated_data['cart']
            cart_product = CartProduct.objects.filter(cart=cart)
            if self.request.user.is_authenticated:
                if cart.client == self.request.user:
                    for cart_products in cart_product:
                        cart_products.product.status = 'В процессе доставки'
                        cart_products.product.save()
                    cart.is_ordered = True
                    cart.save()
                    serializer.save(client=self.request.user, status='На рассмотрении')
                    return Response(serializer.data)
                elif cart.client != self.request.user:
                    return Response({'Вы используете корзину другого клиента'}, status=status.HTTP_403_FORBIDDEN)
            else:
                for cart_products in cart_product:
                    cart_products.product.status = 'В процессе доставки'
                    cart_products.product.save()
                cart.is_ordered = True
                cart.save()
                serializer.save(status='На рассмотрении')
                return Response(serializer.data)
        return Response(serializer.errors)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop('partial', True)
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            if instance.status == 'На рассмотрении':
                instance.save()
                return Response(serializer.data)
            return Response(serializer.errors)


class EmployeeOrderView(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    """Employee order view"""

    def get_serializer_class(self):
        user = self.request.user
        if user.user_type == 'courier':
            return CourierOrderSerializer
        elif user.user_type == 'admin':
            return AdminOrderSerializer

    serializer_class = get_serializer_class
    queryset = Order.objects.all()
    permission_classes = (IsAdmin | IsCourier,)
    filter_backends = [DjangoFilterBackend]
    filter_fields = [
        'status',
        'client__phone',
        'courier__phone',
        'courier__username',
        'creation_datetime',
        'sender_name',
        'sender_phone_number',
    ]

    def get_queryset(self):
        """Filter order queryset by current employee type"""

        user = self.request.user

        if user.user_type == 'courier':
            return self.queryset.filter(status='В ожидании курьера')
        elif user.user_type == 'admin':
            if self.request.query_params.get('accepted_orders'):
                accepted_orders = self.request.query_params.get('accepted_orders').split(',')
                if accepted_orders:
                    queryset = self.queryset.exclude(status__in=accepted_orders)
                    return queryset
            elif self.request.query_params.get('half_year'):
                period = self.request.query_params.get('half_year', 'True')
                today = datetime.datetime.today()
                new_end = today - datetime.timedelta(days=182)
                if period is not None:
                    return self.queryset.filter(creation_datetime__gte=new_end)
            elif self.request.query_params.get('three_months'):
                period = self.request.query_params.get('three_months', 'True')
                today = datetime.datetime.today()
                new_end = today - datetime.timedelta(days=90)
                if period is not None:
                    return self.queryset.filter(creation_datetime__gte=new_end)
            elif self.request.query_params.get('month'):
                period = self.request.query_params.get('month', 'True')
                today = datetime.datetime.today()
                new_end = today - datetime.timedelta(days=30)
                if period is not None:
                    return self.queryset.filter(creation_datetime__gte=new_end)
            return self.queryset.all()

    def perform_update(self, serializer):
        """update courier field value only if request user is courier"""

        if self.request.user.user_type == 'courier':
            serializer.save(courier=self.request.user)
        else:
            serializer.save()

    def update(self, request, *args, **kwargs):
        """Some business logic for order status 'Отменен'"""

        instance = self.get_object()
        partial = kwargs.pop('partial', True)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            order_status = serializer.validated_data['status']
            self.perform_update(serializer)
            if order_status == 'Отменен':
                instance.cart.is_ordered = False
                instance.cart.save()
                cart_product = CartProduct.objects.filter(cart=instance.cart)
                for cart_products in cart_product:
                    cart_products.product.status = 'На продаже'
                    cart_products.product.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class CourierOrderView(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    """Courier order view"""

    serializer_class = CourierOrderSerializer
    queryset = Order.objects.all()
    permission_classes = (IsCourier,)

    def get_queryset(self):
        """Filter orders by current courier"""

        queryset = self.queryset.filter(courier=self.request.user)
        return queryset

    def update(self, request, *args, **kwargs):
        """Some business logic for order status 'Доставлено'"""

        instance = self.get_object()
        partial = kwargs.pop('partial', True)
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            order_status = serializer.validated_data['status']
            serializer.save()
            if order_status == 'Доставлено':
                cart_product = CartProduct.objects.filter(cart=instance.cart)
                for cart_products in cart_product:
                    cart_products.product.status = 'Продан'
                    cart_products.product.sale_datetime = datetime.datetime.now()
                    cart_products.product.save()

                    courier = EmployeeProfile.objects.filter(user=self.request.user)
                    for i in courier:
                        i.salary += instance.courier_percent
                        i.save()
                    florist = EmployeeProfile.objects.filter(user=cart_products.product.florist)
                    for i in florist:
                        i.salary += cart_products.product.florist_percent
                        i.save()

            return Response(serializer.data)
        return Response(serializer.errors)


class OrderStatisticView(ListAPIView):
    """Order statistic view"""

    def list(self, request, *args, **kwargs):
        month = self.request.query_params.get('month')
        three_month = self.request.query_params.get('three_month')
        half_year = self.request.query_params.get('half_year')
        if month:
            duration = datetime.datetime.today() - datetime.timedelta(days=30)
            queryset = Order.objects.filter(creation_datetime__gte=duration, status='Доставлено')\
                .annotate(week=TruncWeek("creation_datetime")).values("week").annotate(total_orders=Count("id"))
            return Response(queryset)

        if three_month:
            duration = datetime.date.today() - datetime.timedelta(days=90)
            queryset = Order.objects.filter(creation_datetime__gte=duration, status='Доставлено')\
                .annotate(week=TruncWeek("creation_datetime")).values("week").annotate(total_orders=Count("id"))
            return Response(queryset)

        if half_year:
            duration = datetime.date.today() - datetime.timedelta(days=182)
            queryset = Order.objects.filter(creation_datetime__gte=duration, status='Доставлено')\
                .annotate(week=TruncMonth("creation_datetime")).values("week").annotate(total_orders=Count("id"))
            return Response(queryset)
        return Response('Статистика заказов магазинов')
