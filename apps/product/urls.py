from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.product.views import (
    ProductView,
    ProductTypeView,
    FlowerView,
    ProductFlowerView,
    ProductImageView,
    FavoriteProductView,
    NewProductView,
    EmployeeHistoryView,
    RevenueStatisticView,
)


app_name = 'apps.product'

router = DefaultRouter()
router2 = DefaultRouter()

router2.register('', FlowerView)
router.register('list', ProductView)
router.register('type', ProductTypeView)
router.register('image', ProductImageView)
router.register('flower', ProductFlowerView)
router.register('favorite', FavoriteProductView)


urlpatterns = [
    path('product/', include(router.urls)),
    path('flower/', include(router2.urls)),
    path('new-product/', NewProductView.as_view()),
    path("employee-history/", EmployeeHistoryView.as_view(), name="employee_history"),
    path("statistic/revenue/", RevenueStatisticView.as_view(), name="revenue_statistic"),

]
