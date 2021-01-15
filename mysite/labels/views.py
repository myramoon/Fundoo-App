"""
Overview: contains api for implementing label management operations
Author: Anam Fazal
Created on: Dec 17, 2020

"""


import logging
import os
from django.db.models import Q
from django.utils.decorators import method_decorator
from accountmanagement.decorators import user_login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LabelSerializer
from .models import Label
from notes import utils
from exceptions.exceptions import CustomError,ExceptionType


# custom exceptions,test case ,put ,delete-delete existing from cache
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
file_handler = logging.FileHandler(os.path.abspath("loggers/log_labels.log"),mode='w')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)



@method_decorator(user_login_required, name='dispatch')
class ManageLabel(APIView):
    """[allows CRUD operations on labels]

    Returns:
        [json]: [list of created/updated/retrieved note(s) with complete details or deletion confirmation and status code]
    """

    def get(self, request, **kwargs):
        """ [displays all labels that requesting user is authorized to see]

        :param request:none
        :param pk: [optional]:[integer] id of the label to be retrieved
        :param kwargs:[mandatory]:[string]authentication token containing user id
        :return:labels owned by the requesting user and status code
        """
        try:
            current_user = kwargs['userid']

            if kwargs.get('pk'):
                if not Label.objects.filter(id=kwargs.get('pk')).exists():
                    raise CustomError(ExceptionType.NonExistentError, "Requested label does not exist")
                label = Label.objects.get(Q(id=kwargs.get('pk')), Q(is_deleted=False),
                                        Q(user=current_user))
                serializer = LabelSerializer(label)

            else:
                labels = Label.objects.filter(Q(user=current_user)).exclude(is_deleted=True)
                serializer = LabelSerializer(labels, many=True)

            result = utils.manage_response(status=True, message='retrieved successfully', data=serializer.data,
                                           log='retrieved labels', logger_obj=logger)
            return Response(result, status.HTTP_200_OK,content_type="application/json")

        except CustomError as e:
            result = utils.manage_response(status=False, message=e.message, log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")

        except Exception as e:
            result = utils.manage_response(status=False, message='Something label went wrong.Please try again.', log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_404_NOT_FOUND,content_type="application/json")

    def post(self, request, **kwargs):
        """[creates new label on requesting user's id]

        :param request: [string]label name
        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return: Created label's details and status code
        """
        try:
            utils.set_user(request, kwargs['userid'])
            serializer = LabelSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):  # Return a 400 response if the data was invalid.
                serializer.save()
                result = utils.manage_response(status=True, message='created successfully', data=serializer.data,
                                               log='created new label', logger_obj=logger)
                return Response(result, status.HTTP_201_CREATED,content_type="application/json")
            else:

                result = utils.manage_response(status=False, message=serializer.errors, log=serializer.errors,
                                               logger_obj=logger)
                return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")
        except Label.DoesNotExist as e:

            result = utils.manage_response(status=False, message='note not found', log=str(e), logger_obj=logger)
            return Response(result, status.HTTP_404_NOT_FOUND,content_type="application/json")
        except Exception as e:

            result = utils.manage_response(status=False, message=str(e), log=str(e), logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")

    def delete(self, request, pk, **kwargs):
        """[soft deletes existing label]

        :param request: none
        :param pk: [mandatory]:[integer] id of the label to be deleted
        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return: Deletion confirmation and status code
        """

        try:
            if not Label.objects.filter(id=pk).exists():
                raise CustomError(ExceptionType.NonExistentError, "Requested label does not exist")
            label = Label.objects.get(Q(id=pk), Q(is_deleted=False),
                                    Q(user=kwargs['userid']))

            label.soft_delete()
            result = utils.manage_response(status=True, message='label deleted successfully',
                                           log=('deleted label with id: {}'.format(pk)), logger_obj=logger)
            return Response(result, status.HTTP_204_NO_CONTENT,content_type="application/json")

        except CustomError as e:
            result = utils.manage_response(status=False, message=e.message, log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")

        except Exception as e:

            result = utils.manage_response(status=False, message='Something went wrong.Please try again.', log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")

    def put(self, request, pk, **kwargs):
        """[updates existing label with new details]

        :param request: one or more label fields with new values
        :param pk: [mandatory]:[integer]id of the label to be updated
        :param kwargs: [mandatory]:[string]authentication token containing user id
        :return: updated label details and status code
        """
        try:
            if not Label.objects.filter(id=pk).exists():
                raise CustomError(ExceptionType.NonExistentError, "Requested label does not exist")
            label = Label.objects.get(Q(id=pk), Q(is_deleted=False),
                                    Q(user=kwargs['userid']))

            serializer = LabelSerializer(label, data=request.data, partial=True)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else:
                result = utils.manage_response(status=False, message=serializer.errors, log=serializer.errors,
                                               logger_obj=logger)
                return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")

            result = utils.manage_response(status=True, message='updated successfully', data=serializer.data,
                                           log='updated note', logger_obj=logger)
            return Response(result, status.HTTP_200_OK,content_type="application/json")

        except CustomError as e:
            result = utils.manage_response(status=False, message=e.message, log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")

        except Exception as e:

            result = utils.manage_response(status=False, message='Something went wrong.Please try again.', log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST, content_type="application/json")


