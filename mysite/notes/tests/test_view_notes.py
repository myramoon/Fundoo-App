from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import pytest
from exceptions.exceptions import CustomError,ExceptionType
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

        self.note_post_url = reverse("manage-notes")
        self.note_url = reverse('manage-specific',args=[1])
        self.note2_url = reverse('manage-specific', args=[2])

        self.note_archived_url = reverse("archived-notes")
        self.single_archived_note_url = reverse('manage-specific-archived',args=[1])

        self.note_pinned_url = reverse("pinned-notes")
        self.single_note_pinned_url = reverse('specific-pinned-note',args=[1])

        self.note_trash_url = reverse("trashed-notes")
        self.single_note_trash_url = reverse('specific-trashed-note',args=[1])

        self.note_search_url = (reverse('searched-notes')) + "?q=" + "my testing note"

        self.valid_registration_data = {'first_name': "anam",
                                        'last_name': "fazal",
                                        'email': "anamfazal94@gmail.com",
                                        'user_name': "anamfazal",
                                        'password': "qwerty12"}

        self.valid_login_data = {
            'email': "anamfazal94@gmail.com",
            'password': "qwerty12"}

        self.valid_label_data = {
            'name': "First Note",
        }

        self.valid_note_data = {
            "title": "my testing note",
            "description": "this is my test note",
            "is_archived": True,
            "is_pinned": True,
            "labels": ["First Note"],
            "collaborators": ["anamfazal94@gmail.com"]
        }

        self.valid_note_put_data = {
            "title": "qwerty note",
            "description": "qwerty description"
        }
        self.invalid_note_data = {
            'title': "note title",
            'description': "this is my description",
            'labels': "Qwerty Note",
            'collaborators': ["abc123@gmail.com"]
        }



        self.valid_note_data2 = {
            "title": "test note 2",
            "description": "this is my 2nd test note",
            "is_archived":True,
            "is_pinned": True,
            "labels": ["First Note"],
            "collaborators": ["anamfazal94@gmail.com"]
        }

        self.valid_trashed_note_data = {
            "title": "my trashed note",
            "description": "this is my trashed note",
            "is_trashed": True,
            "is_pinned": True,
            "labels": ["First Note"],
            "collaborators": ["anamfazal94@gmail.com"]
        }

class NotesTest(Data):
    """
    Test case for validating Notes class with valid and invalid details.
    """

    def test_notes_with_valid_details(self):
        """
        Test case for validating Labels class with valid details.
        """
        client = APIClient()
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_verified = True
        user.is_active = True
        user.save()
        response = client.post(self.login_url, self.valid_login_data, format='json')
        headers = response.data['data']

        response = self.client.post(self.label_url, self.valid_label_data, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = client.post(self.note_post_url, self.valid_note_data, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = client.get(self.note_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.put(self.note_url, self.valid_note_put_data, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.delete(self.note_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_notes_with_invalid_details(self):
        """
        Test case for validating notes class with invalid details.
        """
        client = APIClient()
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_verified = True
        user.is_active = True
        user.save()
        response = client.post(self.login_url, self.valid_login_data, format='json')
        headers = response.data['data']

        response = self.client.post(self.note_post_url, self.invalid_note_data, HTTP_AUTHORIZATION=headers,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(self.note_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(self.note_url, self.valid_note_put_data, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.delete(self.note_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ArchivedViewTest(Data):
    """
    Test case for validating ArchivedViewTest class with valid and invalid details.
    """

    def test_archived_view_for_valid_details(self):
        """
        Test case for checking ManageArchivedNote class with valid details.
        """
        client = APIClient()
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_verified = True
        user.is_active = True
        user.save()
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        headers = response.data['data']
        self.client.post(self.label_url, self.valid_label_data, HTTP_AUTHORIZATION=headers, format='json')
        client.post(self.note_post_url, self.valid_note_data, HTTP_AUTHORIZATION=headers, format='json')
        client.post(self.note_post_url, self.valid_note_data2, HTTP_AUTHORIZATION=headers, format='json')

        response = client.get(self.note_archived_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
       # self.assertEqual(len(response.result['data']), 2)

        response = client.get(self.single_archived_note_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.delete(self.note_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = client.delete(self.note2_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class PinnedViewTest(Data):
    """
    Test case for validating ManagePinnedNote class with valid details.
    """
    def test_pinned_view_for_valid_details(self):
        """
        Test case for validating PinnedView class with valid details.
        """
        client = APIClient()
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_verified = True
        user.is_active = True
        user.save()
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        headers = response.data['data']
        self.client.post(self.label_url, self.valid_label_data, HTTP_AUTHORIZATION=headers, format='json')

        client.post(self.note_post_url, self.valid_note_data, HTTP_AUTHORIZATION=headers, format='json')
        client.post(self.note_post_url, self.valid_note_data2, HTTP_AUTHORIZATION=headers, format='json')

        response = client.get(self.note_pinned_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.single_note_pinned_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.delete(self.note_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = client.delete(self.note2_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SearchViewTest(Data):
    """
    Test case for validating SearchNotes class with valid details.
    """

    def test_search_view_for_valid_details(self):
        """
        Test case for validating SearchNotes class with valid details.
        """
        client = APIClient()
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_verified = True
        user.is_active = True
        user.save()
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        headers = response.data['data']

        self.client.post(self.label_url, self.valid_label_data, HTTP_AUTHORIZATION=headers, format='json')
        client.post(self.note_post_url, self.valid_note_data, HTTP_AUTHORIZATION=headers, format='json')

        response = self.client.get(self.note_search_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.delete(self.note_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)



class TrashViewTest(Data):

    def test_trash_view_for_valid_details(self):
        """
        Test case for validating TrashView class with valid details.
        """
        client = APIClient()
        self.client.post(self.register_url, self.valid_registration_data, format='json')
        user = User.objects.filter(email=self.valid_registration_data['email']).first()
        user.is_verified = True
        user.is_active = True
        user.save()
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        headers = response.data['data']
        self.client.post(self.label_url, self.valid_label_data, HTTP_AUTHORIZATION=headers, format='json')
        client.post(self.note_post_url, self.valid_note_data, HTTP_AUTHORIZATION=headers, format='json')

        response = client.delete(self.note_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.note_trash_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.single_note_trash_url, HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)




































