import json,jwt,os
from django.http import HttpResponse
from rest_framework import status
from notes import utils
from services.cache import Cache
from services.encrypt import Encrypt
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

file_handler = logging.FileHandler('/Users/nusrat/Desktop/VSCODE/Note App/mysite/loggers/log_accounts.log',mode='w')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def user_login_required(view_func):
    """[gets token and fetches user id verifying active status.
        If everything is proper delegates to the requested view]

    :param view_func:[get/post/put/patch/delete view according to request]
    :return: call to view_func if everything is proper else exception messages and status code.
    """
    def wrapper(request, *args, **kwargs):
        try:
            token = request.META['HTTP_AUTHORIZATION']
            decoded_token = Encrypt.decode(token)
            if Cache.getInstance().get("TOKEN_"+str(decoded_token['id'])+"_AUTH").decode("utf-8") == token:
                kwargs['userid'] = decoded_token['id']
                return view_func(request, *args , **kwargs)
            else:
                result = utils.manage_response(status=False,message='User must be logged in',log='User id not found',logger_obj=logger)
                HttpResponse.status_code = status.HTTP_401_UNAUTHORIZED
                return HttpResponse(json.dumps(result),HttpResponse.status_code)
        except jwt.ExpiredSignatureError as e:
            result = utils.manage_response(status=False,message='Activation has expired.Please generate a new token',log=str(e),logger_obj=logger)
            HttpResponse.status_code = status.HTTP_401_UNAUTHORIZED
            return HttpResponse(json.dumps(result), HttpResponse.status_code)
        except jwt.exceptions.DecodeError as e:
            result = utils.manage_response(status=False,message='Please provide a valid token',log=str(e),logger_obj=logger)
            HttpResponse.status_code = status.HTTP_400_BAD_REQUEST
            return HttpResponse(json.dumps(result), HttpResponse.status_code)
        except Exception as e:
            result = utils.manage_response(status=False,message='Something went wrong.Please try again.',log=str(e),logger_obj=logger)
            HttpResponse.status_code = status.HTTP_400_BAD_REQUEST
            return HttpResponse(json.dumps(result), HttpResponse.status_code)

    return wrapper




