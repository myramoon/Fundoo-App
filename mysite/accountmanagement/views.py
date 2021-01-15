"""
Overview: contains logic for apis implementing user account management
Author: Anam Fazal
Created on: Dec 12, 2020 
"""

import os,jwt,logging
from django.utils.decorators import method_decorator
from decouple import config
from .decorators import user_login_required
from .tasks import send_email
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status, views
from rest_framework.response import Response
from .models import Account
from notes import utils
from .serializers import RegisterSerializer, SetNewPasswordSerializer, ResetPasswordEmailRequestSerializer, EmailVerificationSerializer, LoginSerializer,UserDetailsSerializer
from services.cache import Cache
from rest_framework.exceptions import AuthenticationFailed
from services.encrypt import Encrypt

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

file_handler = logging.FileHandler(os.path.abspath("loggers/log_notes.log"),mode='w')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class Login(generics.GenericAPIView):
    """[allows user login after verification and activation]

    Returns:
        [Response]: [username , email and status code]
    """
    serializer_class = LoginSerializer
    
    def post(self, request):
        """[validates user email and password, sets user id in cache]

        :param request:[mandatory]:[string]:email of user
                                   [string]:password
        :return: [dictionary]:status[boolean]
                              response message[string]
                              token[string]
                 [int]:status code
        """
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = Account.objects.get(email=serializer.data['email'])
            token = Encrypt.encode(user.id)

            Cache(config('REDIS_HOST'),config('REDIS_PORT')) #create cache object
            Cache.getInstance().set("TOKEN_"+str(user.id)+"_AUTH", token)

            result = utils.manage_response(status=True ,message = 'Token generated',data = token ,log = 'successfully logged in' , logger_obj = logger)
            return Response(result, status=status.HTTP_200_OK,content_type="application/json")
        except Account.DoesNotExist as e:
            result = utils.manage_response(status=False,message = 'Account does not exist',log=str(e), logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")
        except AuthenticationFailed as e:
            result = utils.manage_response(status=False,message = 'Please enter a valid token' ,log=str(e),logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")
        except Exception as e:
            result = utils.manage_response(status=False,message = 'some other issue.Please try again' ,log=str(e),logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")

@method_decorator(user_login_required, name='dispatch')
class Logout(generics.GenericAPIView):

    def get(self, request,**kwargs):
        """[empties current user's token and notes,labels from cache]

        :param request:
        :return:log out confirmation and status code
        """
        try:
            Cache.getInstance().flushall()
            result = utils.manage_response(status=True ,message = 'Logged out',log = 'successfully logged out' , logger_obj = logger)
            return Response(result,status=status.HTTP_200_OK,content_type="application/json")
        except Exception as e:
            result = utils.manage_response(status=False, message='some other issue.Please try again', log=str(e),
                                           logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")


class Registration(generics.GenericAPIView):
    """[creates new user and sends verification email for activation]
    """
    serializer_class = RegisterSerializer

    def post(self, request):
        """[if registration details are proper then creates new user and sends verification email]

           :param request:[mandatory]:[string]:email of user
                                      [string]:password
                                      [string]:first name of user
                                      [string]:last name of user
                                      [string]:user name of user
           :return: [dictionary]:status[boolean]
                                 response message[string]
                                 posted data[dictionary]
                          [int]:status code
        """
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user_data = serializer.data
            user = Account.objects.get(email=user_data['email'])
            token = RefreshToken.for_user(user).access_token
            absolute_url = request.build_absolute_uri(reverse('email-verify')) + "?token=" + str(token)
            email_body = 'Hi ' + user.user_name + \
                        ', \n Use the link below to verify your email \n' + absolute_url
            data = {'email_body': email_body, 
                    'to_email': user.email,
                    'email_subject': 'Verify your email'}

            send_email.delay(data)
            result = utils.manage_response(status=True ,message = 'Registration successful',data = user_data ,log = 'Created new user',logger_obj=logger)
            return Response(result, status=status.HTTP_201_CREATED,content_type="application/json")
        except Exception as e:
            result = utils.manage_response(status=False,message = 'Some other issue.Please try again' ,log=str(e),logger_obj=logger)
            return Response(result, status.HTTP_400_BAD_REQUEST,content_type="application/json")



class VerifyEmail(views.APIView):
    """[activates user account setting is_active flag true]
    """
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        """[activates user account setting is_active flag true]

        :param request: [string]: generated token
        :return: confirmation message and status code
        """

        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = Account.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.is_active = True
                user.save()
            result = utils.manage_response(status=True ,message='User activated' ,log = 'Activation successful',logger_obj=logger)
            return Response(result, status=status.HTTP_200_OK, content_type="application/json")
        except jwt.ExpiredSignatureError as e:
            result = utils.manage_response(status=False, message='Activation Expired', log=str(e),
                                           logger_obj=logger)
            return Response(result, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except jwt.exceptions.DecodeError as e:
            result = utils.manage_response(status=False, message='Invalid token', log=str(e),
                                           logger_obj=logger)
            return Response(result, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")
        except Exception as e:
            result = utils.manage_response(status=False, message='Something went wrong.Please try again.', log=str(e),
                                           logger_obj=logger)
            return Response(result, status=status.HTTP_400_BAD_REQUEST, content_type="application/json")





class RequestPasswordResetEmail(generics.GenericAPIView):
    """[sends an email to facilitate password reset]
    """
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        """[sends an email to facilitate password reset]

        :param request: [mandatory]:[string]:email of user
        :return: [string] confirmation message
                 email with link to reset password
                 [int] status code
        """

        email = request.data.get('email', '')

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://' + current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                         absurl + "?redirect_url=" + redirect_url
            data = {'email_body': email_body, 
                    'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            send_email.delay(data)
            result = utils.manage_response(status=True ,message = 'We have sent you a link to reset your password' ,data=data,log = 'password link sent successfully',logger_obj=logger)
        return Response(result, status=status.HTTP_200_OK, content_type="application/json")


class SetNewPassword(generics.GenericAPIView):
    """[returns new password when supplied with uid,token and new password]
    """
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        """[returns new password when supplied with uid,token and new password]

        :param request: [mandatory]:[string]: new password
        :return: confirmation message and status code
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = utils.manage_response(status=True, message='Password reset successful',
                                       log='password reset successfully', logger_obj=logger)
        return Response(result, status=status.HTTP_200_OK, content_type="application/json")


class CheckPasswordToken(generics.GenericAPIView):
    """[checks token supplied for setting new password]

    """
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        """[checks token supplied for setting new password]

        Returns:
            [CustomRedirect]: [redirect url or response depending on token validation outcome]
        """

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url + '?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    redirect_url + '?token_valid=True&message=Credentials Valid&uidb64=' + uidb64 + '&token=' + token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

        except DjangoUnicodeDecodeError:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    logger.exception('Exception due to invalid token')
                    return CustomRedirect(redirect_url + '?token_valid=False')

            except UnboundLocalError as e:
                result= utils.manage_response(status=False, message='Token is not valid, please request a new one',
                                       log=str(e), logger_obj=logger)
                return Response(result,
                                status=status.HTTP_400_BAD_REQUEST,content_type="application/json")
            except Exception as e:
                result = utils.manage_response(status=False, message='Something went wrong.Please try again.',
                                               log=str(e), logger_obj=logger)
                return Response(result,status=status.HTTP_400_BAD_REQUEST,content_type="application/json")







