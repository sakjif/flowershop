from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.users.views import (
    RegisterEmployeeView,
    RegisterClientView,
    LoginEmployeeView,
    LoginClientView,
    EmployeeProfileView,
    ShopBranchView,
    EmployeeProfileStatisticView,

)


app_name = "apps.users"

router = DefaultRouter()
router2 = DefaultRouter()
router.register('', EmployeeProfileView)
router2.register('', ShopBranchView)


urlpatterns = [
    path('employee-profile/', include(router.urls)),
    path('shop-branch/', include(router2.urls)),
    path("sign-up/employee/", RegisterEmployeeView.as_view(), name="create_employee"),
    path("sign-up/client/", RegisterClientView.as_view(), name="create_client"),
    path("login/employee/", LoginEmployeeView.as_view(), name="login_employee"),
    path("login/client/", LoginClientView.as_view(), name="login_client"),
    path("statistic/employee/", EmployeeProfileStatisticView.as_view(), name="employee_statistic"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

]
