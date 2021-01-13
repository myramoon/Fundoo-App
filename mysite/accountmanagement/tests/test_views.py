from django.test import RequestFactory
from django.urls import reverse
from mixer.backend.django import mixer
from accountmanagement.views import Registration
from rest_framework import status
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class Data(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.valid_registration_data = {'first_name': "Anam",
                                        'last_name': "Fazal",
                                        'email': "qwertyuiop@gmail.com",
                                        'user_name': "anamfazal",
                                        'password': "zxcvbnm12"}
        self.invalid_registration_data = {'first_name': "qwerty",
                                          'last_name': "uiop",
                                          'email': "dfs",
                                          'user_name': "abc"}

        self.valid_login_data = {
            'email': "qwertyuiop@gmail.com",
            'password': "zxcvbnm12"}

        self.invalid_login_data = {
            'email': "qwerty@gmail.com",
            'password': "uiop"}



class RegistrationTests(Data):

    def test_given_valid_registration_details(self):
        """
        Ensure we can create a new account object.
        """

        response = self.client.post(self.register_url, self.valid_registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_given_invalid_registration_details(self):
        """
        Ensure we cannot create a new account object.
        """

        response = self.client.post(self.register_url, self.invalid_registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class LoginTest(Data):

    def test_given_valid__login_credentials(self):
        """
        Checks whether login occurs when given proper credentials
        """

        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_active = True
        user.save()

        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_given_invalid_credentials_for_login(self):
        """
        Login should fail as invalid credentials are being passed
        """

        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_active = True
        user.save()

        response = self.client.post(self.login_url, self.invalid_login_data, format='json')
        assert response.status_code == 400








        
        