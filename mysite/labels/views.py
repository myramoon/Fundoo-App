"""
Overview: contains logic for note api implementing label management operations
Author: Anam Fazal
Created on: Dec 17, 2020 
"""

import logging
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LabelSerializer
from .models import Label

result = {'status' : "True",
         'message':'updated successfully',
         'data': 'operation successful'}

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
            result['message']='retrieved successfully'
            result['data']=serializer.data
            #logging.debug('validated label list: {}'.format(serializer.data))
            return Response(result,status.HTTP_200_OK)
        except Exception as e:
            result['status']= False
            result['message'] = 'something wrong'
            return Response(result,status.HTTP_400_BAD_REQUEST)  

    def post(self, request):
        """[creates new label]
        Returns:
            [Response]: [result data and status]
        """
        try:
            serializer = LabelSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                result['message']='created successfully'
                result['data']=serializer.data
                logging.debug('validated new label details: {}'.format(serializer.data))
                return Response(result,status.HTTP_201_CREATED)
            else:
                result['status'] = 'False'
                result['message'] = serializer.errors
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Label.DoesNotExist as e:
            result['status']= False
            result['message'] = 'label not found'
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result['status']= False
            result['message'] = 'something wrong'
            return Response(result,status.HTTP_400_BAD_REQUEST)


    

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
        except Label.DoesNotExist:
            result['status']= False
            result['message'] = 'label not found'
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result['status']= False
            result['message'] = 'something wrong'
            return Response(result,status.HTTP_400_BAD_REQUEST)


    def get(self,request,pk):
        """[displays specific label]
        Returns:
            [Response]: [label details]
        """
        try:
            label = self.get_object(pk)
            serializer = LabelSerializer(label, many=False)
            result['message']='retrieved successfully'
            result['data']=serializer.data
            logging.debug('validated label detail: {}'.format(serializer.data))
            return Response(result , status.HTTP_200_OK)
        except Exception as e:
            result['status']= False
            result['message'] = 'something wrong'
            return Response(result,status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """[updates existing label]
        Returns:
            [Response]: [updated details and status]
        """
        try:
            label = self.get_object(pk)
            serializer = LabelSerializer(label, data=request.data)
            if serializer.is_valid():
                serializer.save()
                #logging.debug('validated updated label data: {}'.format(serializer.data))
                result['message']='updated successfully'
                result['data']=serializer.data
                return Response(result, status.HTTP_200_OK)
            else:
                result['status'] = 'False'
                result['data'] = serializer.errors
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Label.DoesNotExist:
            result['status']= False
            result['message'] = 'label not found'
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result['status']= False
            result['message'] = 'something wrong'
            return Response(result,status.HTTP_400_BAD_REQUEST)
                

    def delete(self,request,pk):
        """[deletes existing label]
        Returns:
            [Response]: [confirmation message and status]
        """
        try:
            label = self.get_object(pk)
            label.soft_delete()
            #logging.debug('deleted label with id: {}'.format(pk))
            result['message']='deleted successfully'
            return Response(result,status.HTTP_204_NO_CONTENT)
        except Label.DoesNotExist:
            result['status']= False
            result['message'] = 'label not found'
            return Response(result,status.HTTP_404_NOT_FOUND)
        except Exception as e:
            result['status']= False
            result['message'] = 'something wrong'
            return Response(result,status.HTTP_400_BAD_REQUEST)
            




