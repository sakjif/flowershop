from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperUser(BasePermission):
    """
    Allows access only to superusers.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsClient(BasePermission):
    """
    Allows access only to client
    """

    message = "Sorry but access only for clients"

    def has_permission(self, request, view):
        return bool(
            request.user.is_anonymous
            or request.user.user_type == "client"
        )


class IsOrderClient(BasePermission):
    """
    Allows access only to client
    """

    edit_methods = "DELETE"

    message = "Sorry but access only for clients"

    def has_permission(self, request, view):
        return bool(
            request.user.is_anonymous
            or request.user.user_type == "client"
            and request.method not in self.edit_methods

        )

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True
        if request.user.is_anonymous or request.user.user_type == 'client' and request.method not in self.edit_methods:
            return True
        return False


class IsCourier(BasePermission):
    """
    Allows access only to courier
    """

    message = "Sorry but access only for couriers"

    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type == "courier")


class IsFlorist(BasePermission):
    """
    Allows access only to florist
    """

    message = "Sorry but access only for florists"

    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type == "florist")


class IsAdmin(BasePermission):
    """
    Allows access only to admin
    """

    message = "Sorry but access only for admins"

    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type == "admin")


class IsFloristOrReadOnly(BasePermission):
    """
    Allows access only to florist or give a read only request
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and request.user.user_type == 'florist'
        )


class IsSuperUserOrAdminReadOnly(BasePermission):
    """
    Allows access only to superusers
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and request.user.is_superuser or request.user.user_type == 'admin'
        )


class IsFloristOrAdminOnlyUpdateOrReadOnly(BasePermission):
    """
    Allows access only to florists or administrators for update only.
    """

    edit_methods = ("POST", "DELETE")

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and request.user.user_type == 'florist'
            or request.user.is_authenticated and request.user.user_type == 'admin'
            and request.method not in self.edit_methods
        )

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True
        if obj.florist == request.user:
            return True
        if request.user.is_anonymous and request.method in SAFE_METHODS:
            return True
        if request.user.user_type == 'admin' and request.method not in self.edit_methods:
            return True
        return False

