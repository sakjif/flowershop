from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import mixins, status

from apps.users.permissions import (
    IsSuperUser,
    IsSuperUserOrAdminReadOnly,
)
from apps.users.models import (
    User,
    EmployeeProfile,
    ShopBranch,
)
from apps.users.serializers import (
    RegisterClientSerializer,
    RegisterEmployeeSerializer,
    LoginEmployeeSerializer,
    LoginClientSerializer,
    EmployeeProfileSerializer,
    ShopBranchSerializer,
    EmployeeProfileStatisticSerializer,
)


class RegisterEmployeeView(CreateAPIView):
    """Register employee view"""

    serializer_class = RegisterEmployeeSerializer
    permission_classes = (IsSuperUser,)
    queryset = User.objects.all()


class RegisterClientView(CreateAPIView):
    """Register client view"""

    serializer_class = RegisterClientSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects.all()


class LoginEmployeeView(CreateAPIView):
    """Employee login view"""

    serializer_class = LoginEmployeeSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        phone = request.data["phone"]
        password = request.data["password"]

        user = User.objects.filter(Q(phone=phone, user_type='florist') | Q(phone=phone, user_type='courier')
                                   | Q(phone=phone, user_type='admin') | Q(phone=phone, is_superuser=True)).first()

        if user is None:
            raise AuthenticationFailed("User not found!")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")

        refresh = RefreshToken.for_user(user)
        is_superuser = user.is_superuser
        user_type = user.user_type

        return Response(
            {
                "status": "You successfully logged in",
                "is_superuser": is_superuser,
                "user_type": user_type,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class LoginClientView(CreateAPIView):
    """Client login view"""

    serializer_class = LoginClientSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        phone = request.data["phone"]
        user = User.objects.filter(phone=phone, user_type='client').first()

        if user is None:
            raise AuthenticationFailed("User not found!")

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "status": "You successfully logged in",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class EmployeeProfileView(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """Employee profile view"""

    serializer_class = EmployeeProfileSerializer
    queryset = EmployeeProfile.objects.all().order_by('id')
    permission_classes = (IsSuperUserOrAdminReadOnly, )
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['user__user_type', 'user__is_active', 'user__shop_branch__title', 'user__username', 'user__phone']

    def update(self, request, *args, **kwargs):
        """Updating EmployeeProfile model data and profile password"""

        instance = self.get_object()
        partial = kwargs.pop('partial', True)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            if instance.user:
                instance.user.set_password(instance.user.password)
                instance.user.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """Delete employee profile with data in User model"""

        instance = self.get_object()
        User.objects.filter(pk=instance.user.pk).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopBranchView(ModelViewSet):
    """Shop branch view"""

    serializer_class = ShopBranchSerializer
    queryset = ShopBranch.objects.all()


class EmployeeProfileStatisticView(ListAPIView):
    """Employee profile statistic view"""

    queryset = EmployeeProfile.objects.filter(Q(user__user_type='florist') | Q(user__user_type='courier'))
    serializer_class = EmployeeProfileStatisticSerializer
    filter_backends = [DjangoFilterBackend, ]
    filter_fields = ['user__user_type', ]
