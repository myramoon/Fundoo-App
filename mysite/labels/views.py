"""
Overview: contains logic for note api implementing label management operations
Author: Anam Fazal
Created on: Dec 15, 2020 
"""

import logging
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LabelSerializer
from .models import Label


class ManageLabel(APIView):
    """[allows viewing labels for get and creates new label for post]

    Returns:
        [json]: [list of labels with complete details or creation confirmation and status code]
    """
    serializer_class = LabelSerializer
    def get(self , request):
        """[displays all notes]
        Returns:
            [Response]: [result data and status]
        """
        labels = Label.objects.all()
        serializer = LabelSerializer(labels, many=True)
        result = {'RETRIEVED' : {'status' : "True",
                    'message':'retrieved successfully',
                    'data':serializer.data}}
        #logging.debug('validated label list: {}'.format(serializer.data))
        return Response(result,status.HTTP_200_OK)


    def post(self, request):
        """[creates new label]
        Returns:
            [Response]: [result data and status]
        """
        try:
            serializer = LabelSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                result = {'status' : "True",
                        'message':'created successfully',
                        'data':serializer.data}
                #logging.debug('validated new note details: {}'.format(serializer.data))
                return Response(result,status.HTTP_201_CREATED)
            else:
                result = {'FAILED' : {'status' : 'False',
                            'data':serializer.errors}}
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)

    

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
            return Label.objects.get(id=pk)
        except Label.DoesNotExist:
            return Response('label does not exist',status.HTTP_404_NOT_FOUND)

    def get(self,request,pk):
        """[displays specific label]
        Returns:
            [Response]: [label details]
        """
        label = self.get_object(pk)
        serializer = NoteSerializer(label, many=False)
        result = {'status' : "True",
                    'data':serializer.data}    
        #logging.debug('validated note detail: {}'.format(serializer.data))
        return Response(result , status.HTTP_200_OK)

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
                #logging.debug('validated updated note data: {}'.format(serializer.data))
                result = {'UPDATED' : {'status' : "True",
                        'message':'updated successfully',
                        'data':serializer.data}}
                return Response(result, status.HTTP_200_OK)
            else:
                result = {'FAILED' : {'status' : 'False',
                            'data':serializer.errors}}
                return Response(result,status.HTTP_400_BAD_REQUEST)
        except Label.DoesNotExist:
            return Response('label does not exist',status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        """[deletes existing label]
        Returns:
            [Response]: [confirmation message and status]
        """
        try:
            label = self.get_object(pk)
            label.delete()
            #logging.debug('deleted label with id: {}'.format(pk))
            result = {'DELETED' : {'status' : "True",
                        'message':'deleted successfully'}}
            return Response(result,status.HTTP_204_NO_CONTENT)
        except Label.DoesNotExist:
            return Response('label does not exist',status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status.HTTP_400_BAD_REQUEST)




