from rest_framework import status
from rest_framework.test import APITestCase


class Data(APITestCase):
    def setUp(self):
        self.register_url = 'http://127.0.0.1:8000/register/'
        self.note_post_url = 'http://127.0.0.1:8000/manage-note/'
        

        self.valid_note_data = {'user': 1,
                                'title': "test note1",
                                'description': "test description1",
                                #'labels': ["label1","label4"],
                                'collaborators': ["anamfazal94@gmail.com"],
                                }

        self.valid_registration_data = {'first_name': "Anam",
                                        'last_name': "Fazal",
                                        'email': "anamfazal94@gmail.com",
                                        'user_name': "anamafazal",
                                        'password': "qwerty12"}


class NotesTest(Data):

    def test_given_valid_note_url_for_crud(self):
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        response = self.client.post(self.note_post_url, self.valid_note_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

       