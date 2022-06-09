from django.contrib import admin

from apps.users.models import (
    User,
    EmployeeProfile,
    ShopBranch,
)


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "phone", "username", "user_type", "password", "is_staff", "is_superuser", "is_active"]


admin.site.register(User, UserAdmin)
admin.site.register(EmployeeProfile)
admin.site.register(ShopBranch)
