from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelsTests(TestCase):
    """Test models"""

    def test_create_employee_with_all_data_successfully(self):
        """
        Test create employee user with all data successfully
        :return: None
        """

        username = 'user'
        phone = '0555666444'
        password = 'password'
        employee = get_user_model().objects.create_user(
            username=username, phone=phone, password=password
        )

        self.assertEqual(employee.username, username)
        self.assertEqual(employee.phone, phone)
        # self.assertTrue(employee.set_unusable_password(password))

    def test_create_employee_without_required_data(self):
        """
        Test create employee user without required data (phone and name)
        :return: None
        """

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                username='user', phone=None, password='password'
            )
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                username=None, phone='0555666444', password='password'
            )

    def test_create_client_without_password_successfully(self):
        """
        Test create client user without password successfully
        :return: None
        """

        username = 'user'
        phone = '0555666444'
        password = None
        client = get_user_model().objects.create_user(
            username=username, phone=phone, password=password
        )

        self.assertEqual(client.username, username)
        self.assertEquals(client.phone, phone)
        self.assertFalse(client.check_password(password))

    def test_create_superuser_successfully(self):
        """
        Test create superuser successfully
        :return: None
        """

        superuser = get_user_model().objects.create_superuser(
            username='user', phone='0555666444', password='password'
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertEqual(superuser.user_type, 'admin')

    def test_models_str_method(self):
        """Test user model str method"""

        username = 'user'
        phone = '0555666444'
        password = None
        client = get_user_model().objects.create_user(
            username=username, phone=phone, password=password
        )
        self.assertEqual(str(client), f'{client.phone}')
