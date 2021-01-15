"""
Overview: contains logic for converting emails or label names to ids in request.data
Author: Anam Fazal
Created on: Dec 18, 2020 
"""
import logging
import os
from labels.models import Label
from rest_framework import status
from rest_framework.response import Response
from accountmanagement.models import Account

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

file_handler = logging.FileHandler(os.path.abspath("loggers/log_utils.log"),mode='w')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def set_user(request,user_id):
    """[sets user email to associated user id and modifies request.data]
    :param request: note details
    :param user_id: id of user from decoded token
    :return: -
    Raises:
        Account.DoesNotExist: [if given email isn't found in database]
    """
    request.POST._mutable = True                
    request.data["user"] = user_id
    request.POST._mutable = False


def get_collaborator_list(request):
    """[maps collaborator emails to their user ids and modifies request.data]

    :param request: [optional]:[string]collaborator email(s)
    :return: -
    """
    try:
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
    except Account.DoesNotExist as e:
        result = manage_response(status=False, message='account not found', log=str(e), logger_obj=logger)
        return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")


def get_label_list(request):
    """[maps label titles to their label ids and modifies request.data]

    :param request: [optional]:[string]label name(s)
    :return: -
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
    """[prepares result dictionary to be sent as response]

    :param kwargs: [mandatory]:[int]response status
                               [string]response message
                               [string]log message
                               [object]logger object
                   [optional]:[dict] data for successful requests
    :return: dictionary containing result
    """
    result = {}
    result['status'] = kwargs['status']
    result['message'] = kwargs['message']

    if kwargs['status'] == True:
        if 'data' in kwargs:
            result['data'] = kwargs['data']
        kwargs['logger_obj'].debug('validated data: {}'.format(kwargs['log']))
    else:
        kwargs['logger_obj'].error('error: {}'.format(kwargs['log']))
    return result















