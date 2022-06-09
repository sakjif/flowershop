from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, username, phone, **extra_fields):
        """
        Methode creates user
        :param username: str
        :param phone: str
        :param extra_fields: dict
        :return: User
        """
        if not phone:
            raise ValueError("User must have phone number")
        if not username:
            raise ValueError("User must have username")

        user = self.model(
            username=username,
            phone=phone,
            **extra_fields
        )
        user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, username, phone, password):
        """
        Methode creates superuser
        :param username: str
        :param phone: str
        :param password: str
        :return: superuser
        """
        user = self.model(
            username=username,
            phone=phone,
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.user_type = 'admin'
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User model"""

    user_type_choices = [
        ('client', 'client'),
        ('florist', 'florist'),
        ('courier', 'courier'),
        ('admin', 'admin'),
    ]

    username = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, unique=True)
    image = models.ImageField(null=True, blank=True)
    user_type = models.CharField(max_length=255, choices=user_type_choices, default='client', null=True)
    shop_branch = models.ForeignKey('ShopBranch', on_delete=models.SET_NULL, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return f'{self.phone}'


class EmployeeProfile(models.Model):
    """Employee profile model"""

    working_schedule_choices = [
        ('Дневной', 'Дневной'),
        ('Вечерний', 'Вечерний'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wage = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    salary = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    working_schedule = models.CharField(max_length=255, choices=working_schedule_choices, null=True, blank=True)
    comment = models.CharField(max_length=255, null=True, blank=True)
    user.is_superuser = True
    user.user_type = True

    def __str__(self):
        return f'{self.user}'

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            if instance.is_superuser:
                EmployeeProfile.objects.create(user=instance)
            elif instance.user_type != 'client':
                EmployeeProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        if instance.is_superuser:
            pass
        elif instance.user_type:
            if instance.user_type != 'client':
                instance.employeeprofile.save()
            else:
                pass


class ShopBranch(models.Model):
    """Shop branch model"""

    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    link = models.CharField(max_length=255, null=True)
    contacts = models.CharField(max_length=255)
    working_schedule = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.address}'
