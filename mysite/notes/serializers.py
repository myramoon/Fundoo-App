from rest_framework import serializers
from .models import Note
from labels.models import Label
from accountmanagement.models import Account
from labels.serializers import LabelSerializer
from accountmanagement.serializers import UserDetailsSerializer

class NoteSerializer(serializers.ModelSerializer):   
    #labels = LabelSerializer(required=False, many=True)
    #user = UserDetailsSerializer()
    #collaborators = UserDetailsSerializer(required=False,many=True)
    class Meta:
        model = Note
        fields = '__all__'
        
    
    