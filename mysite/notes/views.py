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
from .serializers import NoteSerializer,LabelSerializer
from .models import Note,Label


#logging.basicConfig(filename='log_notes.log',level=logging.DEBUG, format='%(levelname)s | %(message)s')

#Response related data
response_dict = {'success':['success' , status.HTTP_200_OK], 
                 'something wrong':['some other issue', status.HTTP_400_BAD_REQUEST],
                 'created':['created successfully',status.HTTP_201_CREATED],
                 'updated':['updated successfully',status.HTTP_200_OK],
                 'deleted':['item deleted',status.HTTP_204_NO_CONTENT],
                 }
                

class NotesOverview(APIView):
    """[displays a list of urls that can be used for different operations]

    """
    def get(self , request):
        api_urls = {
            'Note-List': '/note-list/',
            'Note-Detail - View':'/note-detail/<int:pk>/',
            'Note-Create':'/note-create/',
            'Note-Update':'/note-update/<int:pk>/',
            'Note-Delete':'/note-delete/<int:pk>/',
            'Label-List': '/label-list/',
            'Label-Create':'/label-create/',
            'Label-Update':'/label-update/<int:pk>/',
            'Label-Delete':'/label-delete/<int:pk>/',
        }
        return Response(api_urls)

class NotesList(APIView):
    """[displays existing notes]

    Returns:
        [json]: [list of notes with complete details]
    """
    serializer_class = NoteSerializer
    def get(self , request):
        notes = Note.objects.all()
        serializer = NoteSerializer(notes, many=True)
        #logging.debug('validated note list: {}'.format(serializer.data))
        return Response(serializer.data)

class NotesDetail(APIView):
    """[displays existing note with given id]

    Returns:
        [json]: [note details of note with specified id]
    """
    serializer_class = NoteSerializer
    def get(self , request, pk):
        notes = Note.objects.get(id=pk)
        serializer = NoteSerializer(notes, many=False)
        #logging.debug('validated note detail: {}'.format(serializer.data))
        return Response(serializer.data)

class CreateNote(APIView):
    """[creates new note]

    Returns:
        [json]: [creation confirmation and status code]
    """
    serializer_class = NoteSerializer
    def post(self, request):
        try:
            serializer = NoteSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                #logging.debug('validated new note details: {}'.format(serializer.data))
            return Response(response_dict['created'])
        except Exception as e:
            return Response(response_dict['something wrong'])

class UpdateNote(APIView):
    """[updates existing note]

    Returns:
        [json]: [updation confirmation and status code]
    """
    serializer_class = NoteSerializer
    def post(self, request, pk):
        try:
            note = Note.objects.get(id=pk)
            serializer = NoteSerializer(instance=note, data=request.data)

            if serializer.is_valid():
                serializer.save()
                #logging.debug('validated updated note data: {}'.format(serializer.data))
            return Response(response_dict['updated'])
        except Exception as e:
            return Response(response_dict['something wrong'])

class DeleteNote(APIView):
    """[deleted specified note]

    Returns:
        [string]: [message confirming deletion and status code]
    """
    try:
        serializer_class = NoteSerializer
        def delete(self , request , pk):
            note = Note.objects.get(id=pk)
            note.delete()
            #logging.debug('deleted note with id: {}'.format(pk))
            return Response(response_dict['deleted'])
    except Exception as e:
            return Response(response_dict['something wrong'])   


class LabelList(APIView):
    """[displays existing labels]

    Returns:
        [json]: [list of notelabels with complete details]
    """
    serializer_class = LabelSerializer
    def get(self , request):
        labels = Label.objects.all()
        serializer = LabelSerializer(labels, many=True)
        #logging.debug('validated label list: {}'.format(serializer.data))
        return Response(serializer.data)


class CreateLabel(APIView):
    """[creates new label]

    Returns:
        [json]: [creation confirmation and status code]
    """
    serializer_class = LabelSerializer
    try:
        def post(self, request):
            serializer = LabelSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                #logging.debug('validated new label details: {}'.format(serializer.data))
            return Response(response_dict['created'])
    except Exception as e:
            return Response(response_dict['something wrong']) 

class UpdateLabel(APIView):
    """[updates existing label]

    Returns:
        [json]: [updation confirmation and status code]
    """
    serializer_class = LabelSerializer
    try:
        def post(self, request, pk):
            label = Label.objects.get(id=pk)
            serializer = LabelSerializer(instance=label, data=request.data)

            if serializer.is_valid():
                serializer.save()
                #logging.debug('validated new label details: {}'.format(serializer.data))
            return Response(response_dict['updated'])
    except Exception as e:
            return Response(response_dict['something wrong']) 
    

class DeleteLabel(APIView):
    """[deleted specified label]

    Returns:
        [string]: [message confirming deletion and status code]
    """
    try:
        serializer_class = LabelSerializer
        def delete(self , request , pk):
            label = Label.objects.get(id=pk)
            label.delete()
            #logging.debug('deleted label with id: {}'.format(pk))
            return Response(response_dict['deleted'])
    except Exception as e:
            return Response(response_dict['something wrong']) 