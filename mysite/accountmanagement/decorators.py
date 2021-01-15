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

file_handler = logging.FileHandler(os.path.abspath('loggers/log_accounts.log'),mode='w')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def user_login_required(view_func):
    """[gets token and fetches user id verifying active status.
    If everything is proper delegates to the requested view]

    Args:
        view_func ([request]): [the get,post etc view requested]
    """
    def wrapper(request, *args, **kwargs):
        try:
            token = request.META['HTTP_AUTHORIZATION']
            decoded_token = Encrypt.decode(token)
            if Cache.getInstance().get("TOKEN_"+str(decoded_token['id'])+"_AUTH") is not None:
                kwargs['userid'] = decoded_token['id']
                return view_func(request, *args , **kwargs)
                
            
            else:  
                result = utils.manage_response(status=False,message='User must be logged in',log='User id not found',logger_obj=logger)
                return HttpResponse(result,status.HTTP_403_FORBIDDEN)

        except jwt.ExpiredSignatureError as e:
            result = utils.manage_response(status=False,message='Activation has expired.',log=str(e),logger_obj=logger)
            return HttpResponse(json.dumps(result), status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as e:
            result = utils.manage_response(status=False,message='please provide a valid token',log=str(e),logger_obj=logger)
            return HttpResponse(json.dumps(result), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result = utils.manage_response(status=False,message=str(e),log=str(e),logger_obj=logger)
            return HttpResponse(json.dumps(result),status.HTTP_400_BAD_REQUEST)

    return wrapper

    




