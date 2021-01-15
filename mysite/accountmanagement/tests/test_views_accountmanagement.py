from django.urls import reverse
from rest_framework import status
import pytest,json
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class Data(TestCase):
    """
    this class will initialise all the urls and data and it is inherited by other test classes
    """

    def setUp(self):
        """
        this method setup all the url and data which was required by all test cases
        """
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.reset_password_url = reverse("request-reset-email")


        self.valid_registration_data = {'first_name': "anam",
                                        'last_name': "fazal",
                                        'email': "anamfazal94@gmail.com",
                                        'user_name': "anamfazal",
                                        'password': "qwerty12"}

        self.invalid_registration_data = {'first_name': "abc",
                                          'last_name': "def",
                                          'email': "abc123@gmail.com",
                                          'user_name': "abcdef"}
        self.valid_login_data = {
            'email': "anamfazal94@gmail.com",
            'password': "qwerty12"}
        self.invalid_login_data = {
            'email': "123abc@gmail.com",
            'password': "abcdef"}

        self.invalid_registration_data_missing_password = {'first_name': "abc",
                                                           'last_name': "def",
                                                           'email': "abc123@gmail.com",
                                                           'user_name': "abcdef"}

        self.invalid_registration_data_email_missing = {'first_name': "abc",
                                                        'last_name': "def",
                                                        'password': "emailmissing",
                                                        'user_name': "abcdef"}


        self.invalid_test_registration_data_password_less_than_6 = {'first_name': "anam",
                                                                    'last_name': "fazal",
                                                                    'email': "anamfazal@gmail.com",
                                                                    'user_name': "anamfazal",
                                                                    'password': "admin"}
        self.invalid_test_registration_data_user_name_greater_than_20 = {'first_name': "anam",
                                                                         'last_name': "fazal",
                                                                         'email': "anamfazal@gmail.com",
                                                                         'user_name': "qwertyuiopasdfghjklzxcvbnmaz",
                                                                         'password': "adminpass"}
        self.invalid_test_registration_data_last_name_greater_than_20 = {'first_name': "qwerty",
                                                                         'last_name': "qwertyuiopasdfghjklzxcvbnmaz",
                                                                         'email': "anamfazal@gmail.com",
                                                                         'user_name': "anamfazal",
                                                                         'password': "adminpass"}
        self.invalid_test_registration_data_user_name_not_alpha_numeric = {'first_name': "anam",
                                                                           'last_name': "fazal",
                                                                           'email': "anamfazal@gmail.com",
                                                                           'user_name': "anamfazal@def_",
                                                                           'password': "adminpass"}


class RegistrationTests(Data):
    """
    this class will test registration view and match with status_code
    """

    def test_given_valid_details_for_registration(self):
        """
        Ensure we can create a new account object and it returns status code as 201.
        """

        response = self.client.post(self.register_url, self.valid_registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_given_invalid_details_for_registration(self):
        """
        Ensure we cannot create a new account object and returns status code as 400.
        """

        response = self.client.post(self.register_url, self.invalid_registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTest(Data):

    def test_given_valid_credentials_login(self):
        """
        Ensure we can login and return status code as 200.
        """

        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_active = True
        user.save()
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_given_invalid_credentials_for_login(self):
        """
        Ensure we cannot login and returns status code as 400.
        """

        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_active = True
        user.save()

        response = self.client.post(self.login_url, self.invalid_login_data, format='json')
        assert response.status_code == 400

    def test_create_super_user_with_valid_details(self):

        """
        Ensure we can create a new super account object and it returns status code as 201.
        """
        details = User.objects.create_superuser(self.valid_registration_data['first_name'],
                                                self.valid_registration_data['last_name'],
                                                self.valid_registration_data['user_name'],
                                                self.valid_registration_data['email'],
                                                self.valid_registration_data['password'])
        self.assertEqual(details.first_name, self.valid_registration_data['first_name'])

    def test_register_view_with_password_missing(self):
        """
        Ensure we cannot create a new account object and returns status code as 400.
        """

        response = self.client.post(self.register_url, self.invalid_registration_data_missing_password, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_view_with_email_missing(self):
        """
        Ensure we cannot create a new account object and returns status code as 400.
        """

        response = self.client.post(self.register_url, self.invalid_registration_data_email_missing, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_register_view_with_password_length_less_than_6(self):
        """
        Ensure we cannot create a new account object and returns status code as 400.
        """

        response = self.client.post(self.register_url, self.invalid_test_registration_data_password_less_than_6,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_view_with_user_name_length_greater_than_20(self):
        """
        Ensure we cannot create a new account object and returns status code as 400.
        """

        response = self.client.post(self.register_url, self.invalid_test_registration_data_user_name_greater_than_20,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_view_with_last_name_length_greater_than_20(self):
        """
        Ensure we cannot create a new account object and returns status code as 400.
        """

        response = self.client.post(self.register_url, self.invalid_test_registration_data_last_name_greater_than_20,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_view_with_user_name_not_alpha_numeric(self):
        """
        Ensure we cannot create a new account object and returns status code as 400.
        """

        response = self.client.post(self.register_url, self.invalid_test_registration_data_user_name_not_alpha_numeric,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_password_reset_email(self):
        """
        Ensure we can reset password for email and it returns status code as 201.
        """
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_verified = True
        user.save()

        self.logged_in = self.client.post(self.login_url, self.valid_login_data, format='json')
        data = {"email": "anamfazal94@gmail.com"}
        response = self.client.post(self.reset_password_url, data, format='json')
        token = response.data['data']['email_body'].split(" ")[7]
        uidb64 = response.data['data']['email_body'].split(" ")[13]

        valid_data = json.dumps({"password": "qwerty12", "token": token, "uidb64": uidb64})

        response = self.client.patch(reverse("password-reset-complete"), valid_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        invalid_data = json.dumps({"password": "adminpass", "token": token, "uidb64": uidb64 + 's'})

        response = self.client.patch(reverse("password-reset-complete"), invalid_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {"email": "anam@gmail.com"}
        response = self.client.post(self.reset_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)






