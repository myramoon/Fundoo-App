from django.urls import reverse
from rest_framework import status
import pytest
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

        self.label_post_url = reverse("manage-labels")
        self.label_url = reverse("manage-specific-label",args=[1])



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

        self.valid_label_data = {
            'name': "First Note",
        }

        self.valid_label_put_data = {'name': "Test Note",
                                     }
        self.invalid_label_data = {'labelname': "Asdfg Note",
                                   }



class LabelTest(Data):

    def test_given_valid_label_details_for_crud(self):
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_verified = True
        user.is_active = True
        user.save()
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        headers = response.__getitem__(header="HTTP_AUTHORIZATION")
        response = self.client.post(self.label_post_url, self.valid_label_data, HTTP_AUTHORIZATION=headers,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.label_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.label_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_given_invalid_label_details_for_crud(self):
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_verified = True
        user.is_active = True
        user.save()
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        headers = response.__getitem__(header="HTTP_AUTHORIZATION")
        response = self.client.post(self.label_post_url, self.invalid_label_data, HTTP_AUTHORIZATION=headers,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(self.label_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(self.label_url, self.valid_label_put_data, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.delete(self.label_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)





