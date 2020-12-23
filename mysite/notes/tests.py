from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from . import urls
from labels import urls
from mysite import urls


class Data(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.label_create_url = reverse('manage-labels')
        self.note_create_url = reverse('manage-notes')
        self.note_update_url = reverse('manage-specific',args=[1])
        

        self.valid_registration_data = {'first_name': "Anam",
                                        'last_name': "Fazal",
                                        'email': "anamfazal94@gmail.com",
                                        'user_name': "anamfazal",
                                        'password': "qwerty12"}

        self.valid_label_data ={
            "name": "label1"
        }

        self.valid_note_data = {"user": "anamfazal94@gmail.com",
                                "title": "test note1",
                                "description": "test description1",
                                "labels": ["label1"],
                                "collaborators": ["anamfazal94@gmail.com"]
                                }

        self.valid_note_put_data = {'user': "anamfazal94@gmail.com",
                                    'title': "test note",
                                    'description': "Test description",
                                    'labels': ["label1"],
                                    'collaborators': ["anamfazal94@gmail.com"],
                                    }
        
        
        self.invalid_note_data = {'user': "anamfazal@gmail.com",
                                  'description': "test description1",
                                  'labels': ["label"],
                                  'collaborators': 1,
                                  }
        


class NotesTest(Data):


    def test_given_valid_note_url_for_crud(self):
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        self.client.post(self.label_create_url, self.valid_label_data,format='json')
        self.client.post(self.note_create_url, self.valid_note_data, format='json')
        
        response = self.client.get(self.note_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(self.note_create_url, self.valid_note_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.put(self.note_update_url, self.valid_note_put_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.note_update_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_given_invalid_note_details_for_crud(self):

        response = self.client.get(self.note_update_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.note_create_url, self.invalid_note_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(self.note_update_url, self.valid_note_put_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.delete(self.note_update_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
