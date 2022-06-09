from django.urls import path, include

from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.order.views import (
    CartView,
    CartProductView,
    ClientOrderView,
    EmployeeOrderView,
    CourierOrderView,
    OrderStatisticView,
)

app_name = 'apps.order'

router = DefaultRouter()
router2 = SimpleRouter()

router.register('list', CartView)
router.register('cart-product', CartProductView)
router2.register('order/client', ClientOrderView)
router2.register('order/employee', EmployeeOrderView)
router2.register('order/courier', CourierOrderView)

urlpatterns = [
    path('cart/', include(router.urls)),
    path('', include(router2.urls)),
    path('statistic/order/', OrderStatisticView.as_view(), name="order_statistic"),

]
