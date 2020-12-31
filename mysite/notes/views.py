"""
Overview: contains logic for note api implementing note management operations
Author: Anam Fazal
Created on: Dec 15, 2020 
"""

import logging
from django.db.models import Q
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

#response cache,custom exceptions,is_pinned,is_arch,is_trashed,search api,test case
class NotesOverview(APIView):
    """[displays a list of urls that can be used for different operations]
    """
    def get(self , request):
        api_urls = {
            'Note-List|Create': '/manage-note/',
            'Note-Detail-View|Put|Delete':'/manage-note/<int:pk>/',
        }
        return Response(api_urls)


@method_decorator(user_login_required, name='dispatch')
class ManageNote(APIView):
    """[allows viewing notes for get and creates new note for post]

    Returns:
        [json]: [list of notes with complete details or creation confirmation and status code]
    """
    

    serializer_class = NoteSerializer

    def get(self , request,**kwargs):
        """[displays all notes]
        Returns:
            [Response]: [notes result data and status]
        """ 
        try:
        
            notes = Note.objects.filter(Q(user=kwargs['userid'])|Q(collaborators=kwargs['userid'])).exclude(is_deleted=True) 
            serializer = NoteSerializer(notes, many=True)
            result = utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log = serializer.data )

            return Response(result,status.HTTP_200_OK)
        except Exception as e:

            result = utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e))
            return Response(result,status.HTTP_400_BAD_REQUEST)


    def post(self, request , **kwargs):
        """[creates new note]
        Returns:
            [Response]: [result data and status]
        """
        try:
            data = request.data
            utils.set_user(request,kwargs['userid'])
            if data.get('collaborators'):
                utils.get_collaborator_list(request)
            if data.get('labels'):
                utils.get_label_list(request)

            serializer = NoteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):               # Return a 400 response if the data was invalid.
                serializer.save()
                result = utils.manage_response(status=True,message='created successfully',data=serializer.data,log=serializer.data)
                return Response(result,status.HTTP_201_CREATED)
            else:

                result = utils.manage_response(status=False,message=serializer.errors , log=serializer.errors)
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Note.DoesNotExist as e:

            result = utils.manage_response(status=False,message='note not found',log=str(e))
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            
            result = utils.manage_response(status=False,message=str(e),log=str(e))
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
        except Note.DoesNotExist as e:

            result=utils.manage_response(status=False,message='note not found',log=str(e))
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e))
            return Response(result,status.HTTP_400_BAD_REQUEST)

    def get(self,request,pk,**kwargs):
        """[displays specific note]
        Returns:
            [Response]: [note details]
        """
        try:
            note = self.get_object(pk)
            current_user = kwargs['userid']
            user_id = Account.objects.get(email = note.user).id
            collaborator_id = utils.check_collaborator(note,current_user)
            if current_user == user_id or current_user == collaborator_id:
                serializer = NoteSerializer(note)
                result=utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log=serializer.data)
                return Response(result , status.HTTP_200_OK)
            else:
                result=utils.manage_response(status=False,message='user not authorized',log='user not authorized')
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            
            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e))
            return Response(result,status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk,**kwargs):
        """[updates existing note]
        Returns:
            [Response]: [updated details and status]
        """
        try:
            note = self.get_object(pk)
            if kwargs['userid'] == note.user_id:
                data = request.data
                if data.get('collaborators'):
                    utils.get_collaborator_list(request)
                if data.get('labels'):
                    utils.get_label_list(request)
                serializer = NoteSerializer(note, data=request.data , partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                else:
                    result=utils.manage_response(status=False,message=serializer.errors,log= serializer.errors)
                    return Response(result,status.HTTP_400_BAD_REQUEST)
                
                result=utils.manage_response(status=True,message='updated successfully',data=serializer.data,log=serializer.data)
                return Response(result, status.HTTP_200_OK)
            else:
                result=utils.manage_response(status=False,message='no such user for this note',log= 'bad request')
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Note.DoesNotExist as e:

            result=utils.manage_response(status=False,message='note not found',log=str(e))
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:

            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e))
            return Response(result,status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk,**kwargs):
        """[soft deletes existing note]
        Returns:
            [Response]: [confirmation message and status]
        """
        try:
            note = self.get_object(pk)
            user_id = Account.objects.get(email = note.user).id
            if kwargs['userid'] == user_id:
                note.soft_delete()
                result=utils.manage_response(status=True,message='deleted successfully',log=('deleted note with id: {}'.format(pk)))
                return Response(result,status.HTTP_204_NO_CONTENT)
            else:
                result=utils.manage_response(status=False,message='no such user for this note',log= 'bad request')
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Note.DoesNotExist as e:

            result=utils.manage_response(status=False,message='note not found',log=str(e))
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:

            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e))
            return Response(result,status.HTTP_400_BAD_REQUEST)

