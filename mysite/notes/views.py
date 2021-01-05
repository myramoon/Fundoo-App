"""
Overview: contains logic for note api implementing note management operations
Author: Anam Fazal
Created on: Dec 15, 2020 
"""

import logging
from django.db.models import Q
from django.utils.decorators import method_decorator
from accountmanagement.decorators import user_login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import NoteSerializer
from .models import Note
from . import utils
from exceptions.exceptions import (InvalidCredentials, UnVerifiedAccount, EmptyField, LengthError, ValidationError,
                                   Unauthorized)
from services.cache import Cache


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

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
        :param kwargs:[mandatory]:authentication token containing user id
        :return:notes either owned by or of which the requesting user is a collaborator and status code
        """
        try:
            current_user = kwargs['userid']
            if kwargs.get('pk'):
                if Cache.get_cache("NOTE_"+str(kwargs.get('pk'))+"_DETAIL") is not None:
                    note=Cache.get_cache("NOTE_"+str(kwargs.get('pk'))+"_DETAIL")
                    print(note)
                    result=utils.manage_response(status=True,message='retrieved successfully',data=note,log='retrieved specific note from cache',logger_obj=logger)
                    return Response(result , status.HTTP_200_OK)
                else:
                    note = Note.objects.get(Q(id=kwargs.get('pk')),Q(is_trashed=False),
                                Q(user=current_user)|Q(collaborators=current_user))
                    if note is None:
                        raise Unauthorized("No such note exists")
                    serializer = NoteSerializer(note)
                    Cache.set_cache("NOTE_"+str(note.id)+"_DETAIL", str(serializer.data))
            else:
                notes = Note.objects.filter(Q(user=kwargs['userid'])|Q(collaborators=kwargs['userid'])).exclude(is_trashed=True).distinct()
                serializer = NoteSerializer(notes, many=True)

            result=utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log='retrieved notes',logger_obj=logger)
            return Response(result , status.HTTP_200_OK)

        except Unauthorized as e:
            result = utils.manage_response(status=False, message='User not authorized', log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_401_UNAUTHORIZED)

        except Note.DoesNotExist as e:
            result = utils.manage_response(status=False, message='No such note exists', log=str(e),
                                           logger_obj=logger)
            return utils.manage_response(result, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST)


    def post(self, request , **kwargs):
        """[creates new note on requesting user's id]

        :param request: note details like title,description,color,collaborators,labels.
        :param kwargs: [mandatory]:authentication token containing user id
        :return: Created note's details and status code
        """

        try:
            data = request.data

            if 'title' not in data or data['title'] == '' or 'description' not in data or data['description'] == '':
                raise ValidationError("title and description mandatory")
            if len(data['title']) > 140:
                raise LengthError('title should be less than 140 characters')

            utils.set_user(request,kwargs['userid'])
            if data.get('collaborators'):
                utils.get_collaborator_list(request)
            if data.get('labels'):
                utils.get_label_list(request)

            serializer = NoteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):               # Return a 400 response if the data was invalid.
                serializer.save()
                result = utils.manage_response(status=True,message='created successfully',data=serializer.data,log=('created new note with id {}'.format(serializer.data['id'])),logger_obj=logger)
                return Response(result,status.HTTP_201_CREATED)
            else:

                result = utils.manage_response(status=False,message=serializer.errors , log=serializer.errors , logger_obj=logger)
                return Response(result,status.HTTP_400_BAD_REQUEST)

        except Note.DoesNotExist as e:
            result = utils.manage_response(status=False,message='note not found',log=str(e) , logger_obj=logger)
            return Response(result,status.HTTP_404_NOT_FOUND)
        except LengthError as e:
             result = utils.manage_response(status=False, message='Please enter title not greater than 140 characters.', log=str(e), logger_obj=logger)
             return Response(result, status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            result = utils.manage_response(status=False, message='Please enter proper details for each field.',
                                           log=str(e), logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result = utils.manage_response(status=False,message=str(e),log=str(e) , logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk,**kwargs):
        """[soft deletes existing note]

        :param request: none
        :param pk: [mandatory] id of the note to be deleted
        :param kwargs: [mandatory]:authentication token containing user id
        :return: Deletion confirmation and status code
        """

        try:
            note = Note.objects.get(Q(id=pk),Q(is_trashed=False),
                            Q(user=kwargs['userid']))
            if note is None:
                raise Unauthorized('no such note exists')
            note.soft_delete()
            print('dw')
            Cache.delete_cache("NOTE_"+str(note.id)+"_DETAIL")
            print('dleetd')
            result=utils.manage_response(status=True,message='note deleted successfully',log=('deleted note with id: {}'.format(pk)),logger_obj=logger)
            return Response(result,status.HTTP_204_NO_CONTENT)

        except Unauthorized as e:
            result = utils.manage_response(status=False, message='User not authorized', log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_401_UNAUTHORIZED)
        except Note.DoesNotExist as e:

            result=utils.manage_response(status=False,message='note not found',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:

            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk,**kwargs):
        """[updates existing note with new details]

        :param request: one or more note fields with new values
        :param pk: [mandatory]:id of the note to be deleted
        :param kwargs: [mandatory]:authentication token containing user id
        :return: updated notes details and status code
        """

        try:
            
        
            data = request.data
            if data.get('collaborators'):
                utils.get_collaborator_list(request)
            if data.get('labels'):
                utils.get_label_list(request)

            note = Note.objects.get(Q(id=pk),Q(is_trashed=False),
                            Q(user=kwargs['userid']))
            if note is None:
                raise Unauthorized('No such note exists')
            serializer = NoteSerializer(note, data=request.data , partial=True)
    
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                Cache.set_cache("NOTE_" + str(note.id) + "_DETAIL", str(serializer.data))
            else:
                raise ValidationError("Please enter valid details")
                # result=utils.manage_response(status=False,message=serializer.errors,log= serializer.errors,logger_obj=logger)
                # return Response(result,status.HTTP_400_BAD_REQUEST)
            
            result=utils.manage_response(status=True,message='updated successfully',data=serializer.data,log='updated note',logger_obj=logger)
            return Response(result, status.HTTP_200_OK)

        except ValidationError as e:
            result = utils.manage_response(status=False, message='Please enter proper details for each field.',
                                           log=str(e), logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST)
        except Unauthorized as e:
            result = utils.manage_response(status=False, message='User not authorized', log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_401_UNAUTHORIZED)

        except Note.DoesNotExist as e:

            result=utils.manage_response(status=False,message='note not found',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:

            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST)





@method_decorator(user_login_required,name='dispatch')
class ManageArchivedNote(APIView):
    """[shows all archived notes or specific note if pk is passed]

    :return: Response and status code according to operation performed.
    """

    def get(self,request,**kwargs):
        """[shows all archived notes or specific note if pk is passed]

        :param request: none
        :param pk: [mandatory]:id of the note to be retrieved
        :param kwargs: [mandatory]:authentication token containing user id
        :return: archived notes either owned by or of which the requesting user is a collaborator and status code
        """

        try:
            current_user = kwargs['userid']
            if kwargs.get('pk'):
                note = Note.objects.get(Q(id=kwargs.get('pk')),Q(user=current_user)|Q(collaborators=current_user)).filter(is_archived=True).exclude(is_trashed=True)
                serializer = NoteSerializer(note)

            else:
                notes = Note.objects.filter(Q(user=kwargs['userid'])|Q(collaborators=kwargs['userid'])).exclude(is_trashed=True).exclude(is_archived=False).distinct()
                serializer = NoteSerializer(notes, many=True)
            
            result=utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log='retrieved archived note',logger_obj=logger)
            return Response(result , status.HTTP_200_OK)
        except Note.DoesNotExist as e:

            result=utils.manage_response(status=False,message='note not found',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST)

    


@method_decorator(user_login_required,name='dispatch')
class ManagePinnedNotes(APIView):
    """[shows all pinned notes or specific note if pk is passed]

    :return: Response and status code according to operation performed.
    """
    
    def get(self,request,**kwargs):
        """[shows all pinned notes or specific note if pk is passed]

        :param request: none
        :param pk: [mandatory]:id of the note to be retrieved
        :param kwargs: [mandatory]:authentication token containing user id
        :return: pinned notes either owned by or of which the requesting user is a collaborator and status code
        """
        try:
            current_user = kwargs['userid']
            if kwargs.get('pk'):
                note = Note.objects.get(Q(id=kwargs.get('pk')),Q(is_trashed=False),Q(is_pinned=True),
                            Q(user=current_user)|Q(collaborators=current_user))
                serializer = NoteSerializer(note)

            else:
                notes = Note.objects.filter(Q(user=kwargs['userid'])|Q(collaborators=kwargs['userid'])).exclude(is_trashed=True).exclude(is_pinned=False).distinct()
                serializer = NoteSerializer(notes, many=True)
            
            result=utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log='retrieved pinned note',logger_obj=logger)
            return Response(result , status.HTTP_200_OK)
        except Note.DoesNotExist as e:

            result=utils.manage_response(status=False,message='note not found',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_404_NOT_FOUND)

        except Exception as e:
            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST)

    
@method_decorator(user_login_required,name='dispatch')
class ManageTrashedNotes(APIView):
    """[shows all trashed notes or specific note if pk is passed]

    :return: Response and status code according to operation performed.
    """

    def get(self,request,**kwargs):
        """[shows all trashed notes or specific note if pk is passed]

        Args:
            request ([type]): [description]
            pk ([int]): [id of required note]
        """
        try:
            current_user = kwargs['userid']
            if kwargs.get('pk'):
                note = Note.objects.get(Q(id=kwargs.get('pk')),Q(is_trashed=True),Q(user=current_user))
                serializer = NoteSerializer(note)

            else:
                notes = Note.objects.filter(Q(user=kwargs['userid'])).exclude(is_trashed=False)
                serializer = NoteSerializer(notes, many=True)
            
            result=utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log='retrieved trashed note',logger_obj=logger)
            return Response(result , status.HTTP_200_OK)

        except Note.DoesNotExist as e:

            result=utils.manage_response(status=False,message='note not found',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result=utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            return Response(result,status.HTTP_400_BAD_REQUEST)

@method_decorator(user_login_required, name='dispatch')
class SearchNote(APIView):
    """[shows all notes matching by title or description]

    Args:
        APIView ([type]): [description]
    """


    def get(self, request, **kwargs):
        """[shows all trashed notes or specific note if pk is passed]

        :param request: none
        :param pk: [mandatory]:id of the note to be retrieved
        :param kwargs: [mandatory]:authentication token containing user id
        :return: trashed notes either owned by or of which the requesting user is a collaborator and status code
        """
        try:
            current_user = kwargs['userid']
            search_terms = request.data.get('search_term')
            search_term_list = search_terms.split(' ')

            notes = Note.objects.filter(Q(user=current_user) | Q(collaborators=current_user)).exclude(
                is_trashed=True)

            search_query = Q(title__icontains=search_term_list[0]) | Q(description__icontains=search_term_list[0])

            for term in search_term_list[1:]:
                search_query.add((Q(title__icontains=term) | Q(description__icontains=term)), search_query.AND)

            notes = notes.filter(search_query)

            serializer = NoteSerializer(notes, many=True)
            result = utils.manage_response(status=True, message='retrieved notes on the basis of search terms',
                                           data=serializer.data,
                                           log='retrieved searched note', logger_obj=logger)
            return Response(result, status.HTTP_200_OK)

        except Exception as e:
            result = utils.manage_response(status=False, message='Something went wrong.Please try again.',
                                           log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST)
















#if archived is made true,set into archived only.
#exception handling when filter fails for id
#test case ,put ,delete-delete existing from cache
