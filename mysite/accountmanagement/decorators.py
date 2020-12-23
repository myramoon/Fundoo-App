import json
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import status
from rest_framework_jwt.settings import api_settings



def user_login_required(view_func):
    def wrapper(request, *args, **kwargs):

        if request.session:
            user = request.user
            if user.is_authenticated:
                return view_func(request,*args,**kwargs)
            else:
                result = {'success': False, 'message': 'login is required'}
                return HttpResponse(json.dumps(result), status=status.HTTP_400_BAD_REQUEST)
        else:
            result = {'success': False, 'message': 'Users credential not provided..!!'}
            return HttpResponse(json.dumps(result), status=status.HTTP_400_BAD_REQUEST)

    return wrapper





    