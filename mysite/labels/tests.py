from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from . import urls
from mysite import urls


class Data(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.label_create_url = reverse('manage-labels')
        self.label_update_url = reverse('manage-specific-label',args=[1])

        self.valid_label_data = {
                                 'name': "Third Note",
                                 }
        self.valid_label_put_data = {
                                     'name': "First Note",
                                     }
        self.invalid_label_data = {'user': 15,
                                   'label': "Third Note",
                                   }
        self.valid_registration_data = {'first_name': "Anam",
                                        'last_name': "Fazal",
                                        'email': "anamfazal94@gmail.com",
                                        'user_name': "anamfazal",
                                        'password': "qwerty12"}


class LabelsTest(Data):

    def test_given_valid_label_details_for_crud(self):
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        self.client.post(self.label_create_url, self.valid_label_data, format='json')

        response = self.client.get(self.label_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(self.label_create_url, self.valid_label_put_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.put(self.label_update_url, self.valid_label_put_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.label_update_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # def test_given_invalid_label_details_for_crud(self):
    #     response = self.client.post(self.label_post_url, self.invalid_label_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #     response = self.client.get(self.label_url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #     response = self.client.put(self.label_url, self.valid_label_put_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #     response = self.client.delete(self.label_url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)