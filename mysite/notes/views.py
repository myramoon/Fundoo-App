"""
Overview: contains logic for note api implementing note management operations
Author: Anam Fazal
Created on: Dec 15, 2020 
"""

import logging
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from django.utils.decorators import method_decorator
from accountmanagement.decorators import user_login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import NoteSerializer
from .models import Note,Account
from . import utils
from rest_framework.decorators import api_view

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s | %(message)s')

file_handler = logging.FileHandler('log_notes.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class NotesOverview(APIView):
    """[displays a list of urls that can be used for different operations]
    """
    def get(self , request):
        api_urls = {
            'Note-List|Create': '/manage-note/',
            'Note-Detail-View|Put|Delete':'/manage-note/<int:pk>/',
        }
        return Response(api_urls)

#@cache_page(60 * 15)
@method_decorator(user_login_required, name='dispatch')
class ManageNote(APIView):
    """[allows viewing notes for get and creates new note for post]

    Returns:
        [json]: [list of notes with complete details or creation confirmation and status code]
    """
    

    serializer_class = NoteSerializer

    def get(self , request):
        """[displays all notes]
        Returns:
            [Response]: [notes result data and status]
        """ 
        try:
            notes = Note.objects.filter(is_deleted=False) 
            serializer = NoteSerializer(notes, many=True)
            result = utils.manage_response(status=True,message='retrieved successfully',data=serializer.data)
            logger.debug('validated note list: {}'.format(serializer.data))
            return Response(result,status.HTTP_200_OK)
        except Exception as e:
            logger.exception('Something went wrong')
            result = utils.manage_response(status=False,message='something wrong')
            return Response(result,status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        """[creates new note]
        Returns:
            [Response]: [result data and status]
        """
        try:
            data = request.data
            if data.get('user'):
               utils.get_user(request)
            if data.get('collaborators'):
                utils.get_collaborator_list(request)
            if data.get('labels'):
                utils.get_label_list(request)

            serializer = NoteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):               # Return a 400 response if the data was invalid.
                serializer.save()
                result = utils.manage_response(status=True,message='created successfully',data=serializer.data)
                logger.debug('validated new note details: {}'.format(serializer.data))
                return Response(result,status.HTTP_201_CREATED)
            else:
                logger.error('Invalid note details entered')
                result = utils.manage_response(status=False,message=serializer.errors)
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Note.DoesNotExist as e:
            logger.exception('Requested note does not exist')
            result = utils.manage_response(status=False,message='note not found')
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception('Something went wrong')
            result = utils.manage_response(status=False,message='something wrong')
            return Response(result,status.HTTP_400_BAD_REQUEST)


@method_decorator(user_login_required, name='dispatch')
class ManageSpecificNote(APIView):
    """[views,updates existing note or deletes specified note]

    Returns:
        [json]: [updation confirmation and status code]
    """
    serializer_class = NoteSerializer

    def get_object(self , pk):
        """[fetches and returns specific note]
        Args:
            pk ([int]): [id]
        """
        try:
            return Note.objects.get(id = pk, is_deleted = False) 
        except Note.DoesNotExist:
            logger.exception('Requested note does not exist')
            result=utils.manage_response(status=False,message='note not found')
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception('Something went wrong')
            result=utils.manage_response(status=False,message='something wrong')
            return Response(result,status.HTTP_400_BAD_REQUEST)

    def get(self,request,pk):
        """[displays specific note]
        Returns:
            [Response]: [note details]
        """
        try:
            note = self.get_object(pk)
            serializer = NoteSerializer(note)
            result=utils.manage_response(status=True,message='retrieved successfully',data=serializer.data)
            logger.debug('validated note detail: {}'.format(serializer.data))
            return Response(result , status.HTTP_200_OK)
        except Exception as e:
            logger.exception('Something went wrong')
            result=utils.manage_response(status=False,message='something wrong')
            return Response(result,status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk):
        """[updates existing note]
        Returns:
            [Response]: [updated details and status]
        """
        try:
            note = self.get_object(pk)
            data = request.data
            if data.get('user'):
               utils.get_user(request)
            if data.get('collaborators'):
                utils.get_collaborator_list(request)
            if data.get('labels'):
                utils.get_label_list(request)
            serializer = NoteSerializer(note, data=request.data , partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                logger.debug('validated updated note data: {}'.format(serializer.data))
                result=utils.manage_response(status=True,message='updated successfully',data=serializer.data)
                return Response(result, status.HTTP_200_OK)
            else:
                logger.error('Invalid note details entered')
                result=utils.manage_response(status=False,message=serializer.errors)
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Note.DoesNotExist:
            logger.exception('Requested note does not exist')
            result=utils.manage_response(status=False,message='note not found')
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception('Something went wrong')
            result=utils.manage_response(status=False,message='something wrong')
            return Response(result,status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        """[soft deletes existing note]
        Returns:
            [Response]: [confirmation message and status]
        """
        try:
            note = self.get_object(pk)
            note.soft_delete()
            logger.debug('deleted note with id: {}'.format(pk))
            result=utils.manage_response(status=True,message='deleted successfully')
            return Response(result,status.HTTP_204_NO_CONTENT)
        except Note.DoesNotExist:
            logger.exception('Requested note does not exist')
            result=utils.manage_response(status=False,message='note not found')
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception('Something went wrong')
            result=utils.manage_response(status=False,message='something wrong')
            return Response(result,status.HTTP_400_BAD_REQUEST)


