from colorfield.fields import ColorField
from django.db import models
from django.utils import timezone
from accountmanagement.models import Account
from labels.models import Label


class Note(models.Model):
    user = models.ForeignKey(Account , on_delete = models.CASCADE , related_name = 'author', null = True, blank = True)
    title = models.CharField(max_length = 140, blank = True)
    description = models.TextField(blank = True)
    reminder = models.DateTimeField(null = True, blank = True)
    color = ColorField(default='#00F0FF')
    image = models.ImageField( upload_to='note_images/',null = True,blank = True)
    collaborators = models.ManyToManyField(Account , related_name = 'collaborators',  blank = True)
    labels = models.ManyToManyField(Label)
    is_archived = models.BooleanField(default = False, blank = True)
    is_deleted = models.BooleanField(default = False)
    is_pinned = models.BooleanField(default = False, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)


    def __str__(self):
        return self.title

    def soft_delete(self):
        self.is_deleted = True
        self.save()  

    
    

