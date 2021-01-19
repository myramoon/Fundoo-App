"""
Overview: contains logic for note api implementing note management operations
Author: Anam Fazal
Created on: Dec 15, 2020 
"""

import logging
import os
from django.db.models import Q
from django.utils.decorators import method_decorator
from accountmanagement.decorators import user_login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import NoteSerializer
from .models import Note
from . import utils
from exceptions.exceptions import CustomError,ExceptionType
from services.cache import Cache



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

file_handler = logging.FileHandler("/Users/nusrat/Desktop/VSCODE/Note App/mysite/loggers/log_notes.log",mode='w')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

cache=Cache.getInstance()   #get initialised Cache instance from services.Cache

class NotesOverview(APIView):
    """[displays a list of urls that can be used for different operations]
    """
    def get(self , request):
        api_urls = {
            'Note-List|Create': '/manage-note/',
            'Note-Detail-View|Put|Delete':'/manage-note/<int:pk>/',

            'Pinned Note-List|Detail': '/pinned-note/<int:pk>/',
            'Archived Note-List|Detail': '/archived-note/<int:pk>/',
            'Trashed Note-List|Detail': '/trashed-note/<int:pk>/',
            'Searched Note-List|Detail': '/search-note/<int:pk>/',
        }
        return Response(api_urls)


@method_decorator(user_login_required, name='dispatch')
class ManageNotes(APIView):
    """[allows CRUD operations on notes]

    :return: Response and status code according to operation performed.
    """
    def get(self,request,**kwargs):
        """ [displays all notes that requesting user is authorized to see]

        :param request:none
        :param pk: [optional]:[integer] id of the note to be retrieved
        :param kwargs:[mandatory]:[string]authentication token containing user id
        :return:notes either owned by or of which the requesting user is a collaborator and status code
        """
        try:
            current_user = kwargs['userid']
            if kwargs.get('pk'):
                if not Note.objects.filter(id=kwargs.get('pk')).exists():
                    raise CustomError(ExceptionType.NonExistentError, "Requested note does not exist")

                if cache.get("USER_"+str(current_user)+"_NOTE_"+str(kwargs.get('pk'))+"_DETAIL") is not None:
                    note=cache.get("USER_"+str(current_user)+"_NOTE_"+str(kwargs.get('pk'))+"_DETAIL")
                    result=utils.manage_response(status=True,message='retrieved successfully',data=note,log='retrieved specific note from cache',logger_obj=logger)
                    return Response(result ,status.HTTP_200_OK ,content_type="application/json")
                else:
                    note = Note.objects.get(Q(id=kwargs.get('pk')), Q(is_trashed=False),
                                            Q(user=current_user) | Q(collaborators=current_user))
                    serializer = NoteSerializer(note)
                    cache.set("USER_"+str(current_user)+"_NOTE_" + str(note.id) + "_DETAIL", str(serializer.data))


            else:
                notes = Note.objects.filter(Q(user=current_user)|Q(collaborators=current_user)).exclude(is_trashed=True).distinct()
                serializer = NoteSerializer(notes, many=True)

            result=utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log='retrieved notes',logger_obj=logger)
            return Response(result , status.HTTP_200_OK , content_type="application/json")

        except CustomError as e:
            result = utils.manage_response(status=False, message=e.message, log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")
        except Exception as e:
            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST ,content_type="application/json")


    def post(self, request , **kwargs):
        """[creates new note on requesting user's id]

        :param request: note details like title,description,color,collaborators,labels.
        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return: Created note's details and status code
        """

        try:
            data = request.data

            if 'title' not in data or data['title'] == '' or 'description' not in data or data['description'] == '':
                raise CustomError(ExceptionType.ValidationError,"Title and description mandatory")
            if len(data['title']) > 140:
                raise CustomError(ExceptionType.LengthError,"title should be less than 140 characters")

            utils.set_user(request,kwargs['userid'])
            if data.get('collaborators'):
                utils.get_collaborator_list(request)
            if data.get('labels'):
                utils.get_label_list(request)

            serializer = NoteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):               # Return a 400 response if the data was invalid.
                serializer.save()
                result = utils.manage_response(status=True,message='created successfully',data=serializer.data,log=('created new note with id {}'.format(serializer.data['id'])),logger_obj=logger)
                return Response(result,status.HTTP_201_CREATED,content_type="application/json")
            else:
                result = utils.manage_response(status=False,message=serializer.errors , log=serializer.errors , logger_obj=logger)
                return Response(result,status.HTTP_400_BAD_REQUEST,content_type="application/json")

        except CustomError as e:
             result = utils.manage_response(status=False, message=e.message, log=str(e), logger_obj=logger)
             return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")
        except Exception as e:
            result = utils.manage_response(status=False,message=str(e),log=str(e) , logger_obj=logger)
            return Response(result , status.HTTP_400_BAD_REQUEST , content_type="application/json")

    def delete(self,request,pk,**kwargs):
        """[soft deletes existing note]

        :param request: none
        :param pk: [mandatory]:[integer] id of the note to be deleted
        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return: Deletion confirmation and status code
        """

        try:
            current_user=kwargs['userid']
            if not Note.objects.filter(id=pk).exists():
                raise CustomError(ExceptionType.NonExistentError, "Requested note does not exist")
            note = Note.objects.get(Q(id=pk),Q(is_trashed=False),
                            Q(user=current_user))

            note.soft_delete()
            cache.delete("USER_"+str(current_user)+"_NOTE_"+str(note.id)+"_DETAIL")
            result=utils.manage_response(status=True,message='note deleted successfully',log=('deleted note with id: {}'.format(pk)),logger_obj=logger)
            return Response(result,status.HTTP_204_NO_CONTENT , content_type="application/json")

        except CustomError as e:
            result = utils.manage_response(status=False, message=e.message, log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST , content_type="application/json")

        except Exception as e:

            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST,content_type="application/json")


    def put(self, request, pk,**kwargs):
        """[updates existing note with new details]

        :param request: all note fields with or without new values
        :param pk: [mandatory]:[integer]id of the note to be deleted
        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return: updated notes details and status code
        """

        try:

            if not Note.objects.filter(id=pk).exists():
                raise CustomError(ExceptionType.NonExistentError, "Requested note does not exist")
            data = request.data
            if not data.get('collaborators'):
                raise CustomError(ExceptionType.MissingFieldError, "Please enter collaborators")
            utils.get_collaborator_list(request)
            if not data.get('labels'):
                raise CustomError(ExceptionType.MissingFieldError, "Please enter labels")
            utils.get_label_list(request)

            current_user=kwargs['userid']
            note = Note.objects.get(Q(id=pk),Q(is_trashed=False),
                            Q(user=current_user))

            serializer = NoteSerializer(note, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                if cache.get("USER_"+str(current_user)+"_NOTE_" + str(note.id) + "_DETAIL"):
                    cache.delete("USER_"+str(current_user)+"_NOTE_" + str(note.id) + "_DETAIL")
                cache.set("USER_"+str(current_user)+"_NOTE_" + str(note.id) + "_DETAIL", str(serializer.data))
            else:
                raise CustomError(ExceptionType.ValidationError,"Please enter valid details")

            result=utils.manage_response(status=True,message='updated successfully',data=serializer.data,log='updated note',logger_obj=logger)
            return Response(result, status.HTTP_200_OK,content_type="application/json")

        except CustomError as e:
            result = utils.manage_response(status=False, message=e.message,
                                           log=str(e), logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")

        except Exception as e:

            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST,content_type="application/json")

    def patch(self, request, pk, **kwargs):
        """[updates existing note with new details]

        :param request: one or more note fields with new values
        :param pk: [mandatory]:[integer]id of the note to be deleted
        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return: updated notes details and status code
        """

        try:

            if not Note.objects.filter(id=pk).exists():
                raise CustomError(ExceptionType.NonExistentError, "Requested note does not exist")
            data = request.data
            if data.get('collaborators'):
                utils.get_collaborator_list(request)
            if data.get('labels'):
                utils.get_label_list(request)

            current_user = kwargs['userid']
            note = Note.objects.get(Q(id=pk), Q(is_trashed=False),Q(user=current_user))
            serializer = NoteSerializer(note, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                if cache.get("USER_" + str(current_user) + "_NOTE_" + str(note.id) + "_DETAIL"):
                    cache.delete("USER_" + str(current_user) + "_NOTE_" + str(note.id) + "_DETAIL")
                cache.set("USER_" + str(current_user) + "_NOTE_" + str(note.id) + "_DETAIL", str(serializer.data))
            else:
                raise CustomError(ExceptionType.ValidationError, "Please enter valid details")
            result = utils.manage_response(status=True, message='updated successfully', data=serializer.data,
                                           log='updated note', logger_obj=logger)
            return Response(result, status.HTTP_200_OK, content_type="application/json")

        except CustomError as e:
            result = utils.manage_response(status=False, message=e.message,
                                           log=str(e), logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")

        except Exception as e:

            result = utils.manage_response(status=False, message='Something went wrong.Please try again.', log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")


@method_decorator(user_login_required,name='dispatch')
class ManageArchivedNote(APIView):
    """[shows all archived notes or specific note if pk is passed]

    :return: Response and status code according to operation performed.
    """

    def get(self,request,*args,**kwargs):
        """[shows all archived notes or specific note if pk is passed]

        :param request: none
        :param pk: [optional]:[integer]id of the archived note to be retrieved
        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return: archived notes either owned by or of which the requesting user is a collaborator and status code
        """

        try:
            current_user = kwargs['userid']
            if kwargs.get('pk'):
                if not Note.objects.filter(id=kwargs.get('pk')).exists():
                    raise CustomError(ExceptionType.NonExistentError, "Requested note does not exist")

                note = Note.objects.get(Q(id=kwargs.get('pk')),Q(is_archived=True),Q(is_trashed=False),
                                        Q(user=current_user) | Q(collaborators=current_user))
                serializer = NoteSerializer(note)



            else:
                notes = Note.objects.filter(Q(user=kwargs['userid'])|Q(collaborators=kwargs['userid'])).exclude(is_trashed=True).exclude(is_archived=False).distinct()
                serializer = NoteSerializer(notes, many=True)
            
            result=utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log='retrieved archived note',logger_obj=logger)
            return Response(result , status.HTTP_200_OK ,content_type="application/json")
        except CustomError as e:
            result=utils.manage_response(status=False,message=e.message,log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST,content_type="application/json")
        except Exception as e:
            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST,content_type="application/json")

    

@method_decorator(user_login_required,name='dispatch')
class ManagePinnedNotes(APIView):
    """[shows all pinned notes or specific note if pk is passed]

    :return: Response and status code according to operation performed.
    """
    
    def get(self,request,**kwargs):
        """[shows all pinned notes or specific note if pk is passed]

        :param request: none
        :param pk: [optional]:[integer]id of the pinned note to be retrieved
        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return: pinned notes either owned by or of which the requesting user is a collaborator and status code
        """
        try:
            current_user = kwargs['userid']
            if kwargs.get('pk'):
                if not Note.objects.filter(id=kwargs.get('pk')).exists():
                    raise CustomError(ExceptionType.NonExistentError, "Requested note does not exist")

                note = Note.objects.get(Q(id=kwargs.get('pk')),Q(is_trashed=False),Q(is_pinned=True),
                            Q(user=current_user)|Q(collaborators=current_user))
                serializer = NoteSerializer(note)

            else:
                notes = Note.objects.filter(Q(user=kwargs['userid'])|Q(collaborators=kwargs['userid'])).exclude(is_trashed=True).exclude(is_pinned=False).distinct()
                serializer = NoteSerializer(notes, many=True)
            
            result=utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log='retrieved pinned note',logger_obj=logger)
            return Response(result , status.HTTP_200_OK , content_type="application/json")

        except CustomError as e:
            result=utils.manage_response(status=False,message=e.message,log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST ,content_type="application/json")

        except Exception as e:
            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST , content_type="application/json")

    
@method_decorator(user_login_required,name='dispatch')
class ManageTrashedNotes(APIView):
    """[shows all trashed notes or specific note if pk is passed]

    :return: Response and status code according to operation performed.
    """

    def get(self,request,**kwargs):
        """[shows all trashed notes or specific note if pk is passed]

        :param request: none
        :param pk: [optional]:[integer]id of the trashed note to be retrieved
        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return: trashed note(s) owned by requesting user and status code
        """
        try:
            current_user = kwargs['userid']
            if kwargs.get('pk'):
                if not Note.objects.filter(id=kwargs.get('pk')).exists():
                    raise CustomError(ExceptionType.NonExistentError, "Requested note does not exist")

                note = Note.objects.get(Q(id=kwargs.get('pk')),Q(is_trashed=True),Q(user=current_user))
                serializer = NoteSerializer(note)

            else:
                notes = Note.objects.filter(Q(user=kwargs['userid'])).exclude(is_trashed=False)
                serializer = NoteSerializer(notes, many=True)
            
            result=utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log='retrieved trashed note',logger_obj=logger)
            return Response(result , status.HTTP_200_OK , content_type="application/json")

        except CustomError as e:
            result=utils.manage_response(status=False,message=e.message,log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST,content_type="application/json")
        except Exception as e:
            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST,content_type="application/json")



@method_decorator(user_login_required, name='dispatch')
class SearchNote(APIView):
    """[shows all notes matching by title or description]

    Args:
        APIView ([type]): [description]
    """


    def get(self, request, **kwargs):
        """[shows all trashed notes or specific note if pk is passed]

        :param request: [mandatory]:[string]search term containing part of title or description
        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return: matching notes either owned by or of which the requesting user is a collaborator and status code
        """

        try:
            current_user = kwargs['userid']
            search_terms = request.query_params.get('q')
            if search_terms is '':
                raise CustomError(ExceptionType.ValidationError,"Please enter a search term")
            search_term_list = search_terms.split(' ')

            notes = Note.objects.filter(Q(user=current_user) | Q(collaborators=current_user)).exclude(
                is_trashed=True)

            search_query = Q(title__icontains=search_term_list[0]) | Q(description__icontains=search_term_list[0])

            for term in search_term_list[1:]:
                search_query.add((Q(title__icontains=term) | Q(description__icontains=term)), search_query.AND)

            notes = notes.filter(search_query)
            serializer = NoteSerializer(notes, many=True)
            if serializer.data == []:
                raise CustomError(ExceptionType.NonExistentError, "Search term didn't match any existing note.Please try again")

            result = utils.manage_response(status=True, message='retrieved notes on the basis of search terms',
                                           data=serializer.data,
                                           log='retrieved searched note', logger_obj=logger)
            return Response(result, status.HTTP_200_OK, content_type="application/json")

        except CustomError as e:
            result=utils.manage_response(status=False,message=e.message,log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_404_NOT_FOUND,content_type="application/json")
        except Exception as e:
            result = utils.manage_response(status=False, message='Something went wrong.Please try again.',
                                           log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")

























