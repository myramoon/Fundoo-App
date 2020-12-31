"""
Overview: contains logic for note api implementing label management operations
Author: Anam Fazal
Created on: Dec 17, 2020 
"""

import logging
from django.shortcuts import render
from django.utils.decorators import method_decorator
from accountmanagement.decorators import user_login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from notes import utils
from .serializers import LabelSerializer
from .models import Label

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s | %(message)s')

file_handler = logging.FileHandler('log_labels.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

@method_decorator(user_login_required, name='dispatch')
class ManageLabel(APIView):
    """[allows viewing labels for get and creates new label for post]

    Returns:
        [json]: [list of labels with complete details or creation confirmation and status code]
    """
    serializer_class = LabelSerializer
    def get(self , request):
        try:
        
            """[displays all notes]
            Returns:
                [Response]: [result data and status]
            """
            labels = Label.objects.filter(is_deleted=False) 
            serializer = LabelSerializer(labels, many=True)
            result = utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log=serializer.data)
            return Response(result,status.HTTP_200_OK)
        except Exception as e:
            result = utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e))
            return Response(result,status.HTTP_400_BAD_REQUEST)  

    def post(self, request):
        """[creates new label]
        Returns:
            [Response]: [label data and status]
        """

        try:
            serializer = LabelSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                result = utils.manage_response(status=True,message='label created successfully',data=serializer.data,log=serializer.data)
                return Response(result,status.HTTP_201_CREATED)
            else:

                result = utils.manage_response(status=False,message=serializer.errors,log=serializer.errors)
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Label.DoesNotExist as e:

            result = utils.manage_response(status=False,message='label not found',log=str(e))
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            
            result = utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e))
            return Response(result,status.HTTP_400_BAD_REQUEST)


    
@method_decorator(user_login_required, name='dispatch')
class ManageSpecificLabel(APIView):
    """[views,updates existing label or deletes specified label]

    Returns:
        [json]: [updation confirmation and status code]
    """
    serializer_class = LabelSerializer

    def get_object(self , pk):
        """[fetches and returns specific label]
        Args:
            pk ([int]): [id]
        """
        try:
            return Label.objects.get(id = pk, is_deleted = False) 
        except Label.DoesNotExist as e:
            result = utils.manage_response(status=False,message='label not found',log=str(e))
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            
            result = utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e))
            return Response(result,status.HTTP_400_BAD_REQUEST)


    def get(self,request,pk):
        """[displays specific label]
        Returns:
            [Response]: [label details]
        """
        try:
            label = self.get_object(pk)
            serializer = LabelSerializer(label, many=False)
            result = utils.manage_response(status=True,message='retrieved successfully',data=serializer.data,log=serializer.data)
            return Response(result , status.HTTP_200_OK)
        except Exception as e:
            result = utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e))
            return Response(result,status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """[updates existing label]
        Returns:
            [Response]: [updated details and status]
        """

        try:
            label = self.get_object(pk)     #validate type of pk request.data
            serializer = LabelSerializer(label, data=request.data)
            if serializer.is_valid():
                serializer.save()
                
                result = utils.manage_response(status=True,message='updated successfully',data=serializer.data,log=serializer.data)
                return Response(result, status.HTTP_200_OK)
            else:
                result = utils.manage_response(status=True,message=serializer.errors,log=serializer.errors)
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Label.DoesNotExist as e:
        
            result = utils.manage_response(status=False,message='label not found',log=str(e))
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            
            result = utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e))
            return Response(result,status.HTTP_400_BAD_REQUEST)
                

    def delete(self,request,pk):
        """[deletes existing label]
        Returns:
            [Response]: [confirmation message and status]
        """
        try:
            label = self.get_object(pk)
            label.soft_delete()

            result = utils.manage_response(status=True,message='deleted successfully',log=('deleted label with id: {}'.format(pk)))
            return Response(result,status.HTTP_204_NO_CONTENT)
        except Label.DoesNotExist as e:

            result = utils.manage_response(status=False,message='label not found',log=str(e))
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            
            result = utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e))
            return Response(result,status.HTTP_400_BAD_REQUEST)
            




