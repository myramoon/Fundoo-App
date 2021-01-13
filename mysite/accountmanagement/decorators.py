import json,jwt
from django.http import HttpResponse
from rest_framework import status
from .models import Account
from notes import utils
from rest_framework_jwt.settings import api_settings
from services.cache import Cache
from services.encrypt import Encrypt
import logging


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
            if Cache.get_cache("TOKEN_"+str(decoded_token['id'])+"_AUTH") is not None:
                request.user = Account.objects.get(id=decoded_token['id'])
                return view_func(request, *args, **kwargs)
            result = utils.manage_response(status=False,message='User must be logged in')
            return HttpResponse(json.dumps(result), status=status.HTTP_400_BAD_REQUEST)
        except jwt.ExpiredSignatureError as e:
            result = utils.manage_response(status=False,message='Activation has expired.',error=e)
            #logging.exception('{} exception = {}, status_code = {}'.format(result, str(e), status.HTTP_400_BAD_REQUEST))
            return HttpResponse(json.dumps(result), status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as e:
            result = utils.manage_response(status=False,message='please provide a valid token',error=e)
            #logging.exception('{}, exception = {}, status_code = {}'.format(result, str(e), status.HTTP_400_BAD_REQUEST))
            return HttpResponse(json.dumps(result), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result = utils.manage_response(status=False,message='Something went wrong.Please try again.',error=e)
            return HttpResponse(json.dumps(result),status.HTTP_400_BAD_REQUEST)

    return wrapper

    




