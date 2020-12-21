"""
Overview: contains logic for note api implementing note management operations
Author: Anam Fazal
Created on: Dec 15, 2020 
"""

import logging
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import NoteSerializer
from .models import Note,Account
from . import utils
from rest_framework.decorators import api_view

#logging.basicConfig(filename='log_notes.log',level=logging.DEBUG, format='%(levelname)s | %(message)s')


class NotesOverview(APIView):
    """[displays a list of urls that can be used for different operations]
    """
    def get(self , request):
        api_urls = {
            'Note-List|Create': '/manage-note/',
            'Note-Detail-View|Put|Delete':'/manage-note/<int:pk>/',
        }
        return Response(api_urls)

class ManageNote(APIView):
    """[allows viewing notes for get and creates new note for post]

    Returns:
        [json]: [list of notes with complete details or creation confirmation and status code]
    """
    serializer_class = NoteSerializer
    def get(self , request):
        """[displays all notes]
        Returns:
            [Response]: [result data and status]
        """ 
        notes = Note.objects.filter(is_deleted=False) 
        serializer = NoteSerializer(notes, many=True)
        result = {'RETRIEVED' : {'status' : "True",
                    'message':'retrieved successfully',
                    'data':serializer.data}}
        #logging.debug('validated note list: {}'.format(serializer.data))
        return Response(result,status.HTTP_200_OK)


    def post(self, request):
        """[creates new note]
        Returns:
            [Response]: [result data and status]
        """
        try:
            if request.data.get('user'):
                utils.get_user(request)
            if request.data.get('collaborators'):
                utils.get_collaborator_list(request)
            if request.data.get('labels'):
                utils.get_label_list(request)

            serializer = NoteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):               # Return a 400 response if the data was invalid.
                serializer.save()
                result = {'status' : True,
                        'message':'created successfully',
                        'data':serializer.data}
                #logging.debug('validated new note details: {}'.format(serializer.data))
                return Response(result,status.HTTP_201_CREATED)
            else:
                result = {'status' : 'False',
                        'message':serializer.errors}
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Note.DoesNotExist as e:
            return Response('note does not exist',status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)


    

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
            return Response('note does not exist',status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)

    def get(self,request,pk):
        """[displays specific note]
        Returns:
            [Response]: [note details]
        """
        try:
            note = self.get_object(pk)
            serializer = NoteSerializer(note)
            result = {'status' : "True",
                        'data':serializer.data}    
            #logging.debug('validated note detail: {}'.format(serializer.data))
            return Response(result , status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk):
        """[updates existing note]
        Returns:
            [Response]: [updated details and status]
        """
        try:
            note = self.get_object(pk)
            if request.data.get('user'):
                utils.get_user(request)
            if request.data.get('collaborators'):
                utils.get_collaborator_list(request)
            if request.data.get('labels'):
                utils.get_label_list(request)
            serializer = NoteSerializer(note, data=request.data , partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                #logging.debug('validated updated note data: {}'.format(serializer.data))
                result = {'UPDATED' : {'status' : "True",
                        'message':'updated successfully',
                        'data':serializer.data}}
                return Response(result, status.HTTP_200_OK)
            else:
                result = {'FAILED' : {'status' : 'False',
                            'data':serializer.errors}}
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Note.DoesNotExist:
            return Response('note does not exist',status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        """[soft deletes existing note]
        Returns:
            [Response]: [confirmation message and status]
        """
        try:
            note = self.get_object(pk)
            note.soft_delete()
            #logging.debug('deleted note with id: {}'.format(pk))
            result = {'status' : "True",
                        'message':'deleted successfully'}
            return Response(result,status.HTTP_204_NO_CONTENT)
        except Note.DoesNotExist:
            return Response('note does not exist',status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)



