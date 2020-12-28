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
                                        'email': "anamfazal@gmail.com",
                                        'user_name': "anamfazal",
                                        'password': "qwerty12"}
        self.invalid_registration_data = {'first_name': "qwerty",
                                          'last_name': "uiop",
                                          'email': "dfs",
                                          'user_name': "abc"}


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

















        # self.valid_login_data = {
        #     'email': "anamfazal@gmail.com",
        #     'password': "qwerty12"}
        # self.invalid_login_data = {
        #     'email': "qwerty@gmail.com",
        #     'password': "uiop"}
