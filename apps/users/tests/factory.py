import factory

from apps.users import models


class ShopBranchFactory(factory.django.DjangoModelFactory):
    """Fake ShopBranch model"""

    class Meta:
        model = models.ShopBrnch

    title = 'Юнусалиева 123'
    address = 'Юнусалиева 123'
    longitude = '123412'
    latitude = '234235'
    contacts = '0555555555'
    working_schedule = 'пн-пт с 9.00-22.00'


class UserFactory(factory.django.DjangoModelFactory):
    """Fake User model"""

    class Meta:
        model = models.User

    username = 'Anton'
    phone = '0555643343'
    user_type = 'florist'
    shop_branch = factory.SubFactory(ShopBranchFactory)
