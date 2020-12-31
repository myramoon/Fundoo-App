"""
Overview: contains logic for converting emails or label names to ids in request.data
Author: Anam Fazal
Created on: Dec 18, 2020 
"""
import logging
from labels.models import Label
from accountmanagement.models import Account

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s | %(message)s')

file_handler = logging.FileHandler('log_accountmanagement.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def set_user(request,user_id):
    """[sets user email to associated user id and modifies request.data]
    Args:
        request ([QueryDict]): [post data]
    Raises:
        Account.DoesNotExist: [if given email isn't found in database]
    """
    request.POST._mutable = True                
    request.data["user"] = user_id
    request.POST._mutable = False


def get_collaborator_list(request):
    """[maps collaborator emails to their user ids and modifies request.data]

    Args:  
        request ([QueryDict]): [post data]
    """
    request.POST._mutable = True
    collaborators_list=[]                                           #holds ids associated to label names
    for collaborator_email in request.data.get('collaborators'):
        collab_qs = Account.objects.filter(email=collaborator_email)
        if not collab_qs:
            raise Account.DoesNotExist('No such user account exists')
        if collab_qs.exists() and collab_qs.count() == 1:
            collab_obj = collab_qs.first()                         #assign object from queryset 
            collaborators_list.append(collab_obj.id)               # append object id of the obtained object to list
    request.data["collaborators"] = collaborators_list
    request.POST._mutable = False

def get_label_list(request):
    """[maps label titles to their label ids and modifies request.data]

    Args:
        request ([QueryDict]): [post data]
    """ 
    request.POST._mutable = True
    label_list=[]                                           #holds ids associated to label names
    for label_name in request.data.get('labels'):
        label_qs = Label.objects.filter(name=label_name)
        if not label_qs:
            raise Label.DoesNotExist('No such label exists')
        if label_qs.exists() and label_qs.count() == 1:
            label_obj = label_qs.first()                         #assign object from queryset 
            label_list.append(label_obj.id)               # append object id of the obtained object to list
    request.data["labels"] = label_list
    request.POST._mutable = False
    
    

def manage_response(**kwargs):

    result = {}
    #if 'data' in kwargs:
    if kwargs['status'] == True:
        result['status']=kwargs['status']
        result['message']=kwargs['message']
        if 'data' in kwargs:
            result['data']=kwargs['data']
        logger.debug('validated data: {}'.format(kwargs['log']))
    else:
        result['status']=kwargs['status']
        result['message']=kwargs['message']
        logger.error(kwargs['log'])
    return result

def check_collaborator(note,current_user):
    
    collaborator_qs = note.collaborators.all()
    for collaborator in collaborator_qs:
        if collaborator.id == current_user:
            return collaborator.id
    













#from rest_framework.views import exception_handler

# def custom_exception_handler(exc, context):
#      #Call REST framework's default exception handler first, 
#     #to get the standard error response.
#     response = exception_handler(exc, context)

#     # Now add the HTTP status code to the response.
#     if response is not None:
#         response.data['status_code'] = response.status_code

#     return response