"""
Overview: contains logic for apis implementing user account management
Author: Anam Fazal
Created on: Dec 12, 2020 
"""

import os,jwt
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Account
from notes import utils
from .serializers import RegisterSerializer, SetNewPasswordSerializer, ResetPasswordEmailRequestSerializer, EmailVerificationSerializer, LoginSerializer,UserDetailsSerializer
from .utils import Util 
from services.cache import Cache
from decouple import config
from rest_framework.exceptions import AuthenticationFailed
from services.encrypt import Encrypt

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
        Returns:
            [dictionary]: [token]
        """
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = Account.objects.get(email=serializer.data['email'])
            token = Encrypt.encode(user.id)
            #token = jwt.encode({"id": user.id}, "secret", algorithm="HS256").decode('utf-8')
            Cache.set_cache("TOKEN_"+str(user.id)+"_AUTH", token)
            result = utils.manage_response(status=True ,message = 'Token generated',data = token ,log = serializer.data)
            return Response(result, status=status.HTTP_200_OK)
        except Account.DoesNotExist as e:
            result = utils.manage_response(status=False,message = 'Account does not exist',log=str(e))
            return Response(result, status.HTTP_400_BAD_REQUEST)
        except AuthenticationFailed as e:
            result = utils.manage_response(status=False,message = 'Please enter a valid token' ,log=str(e))
            return Response(result, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result = utils.manage_response(status=False,message = 'some other issue.Please try again' ,log=str(e))
            return Response(result, status.HTTP_400_BAD_REQUEST)


class Registration(generics.GenericAPIView):
    """[creates new user and sends verification email for activation]
    """
    serializer_class = RegisterSerializer

    def post(self, request):
        """[if registration details are proper then creates new user and sends verification email]

        Returns:
            [Response]: [user data after registration]
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

            Util.send_email(data)
            result = utils.manage_response(status=True ,message = 'Registration successful',data = user_data ,log = serializer.data)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            result = utils.manage_response(status=False,message = 'some other issue.Please try again' ,log=str(e))
            return Response(result, status.HTTP_400_BAD_REQUEST)



class VerifyEmail(views.APIView):
    """[sends verification email for activation of new user]
    """
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        """[sends verification email for activation of new user]

        Returns:
            [Response]: [activation status message]
        """
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = Account.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.is_active = True
                user.save()
            result = utils.manage_response(status=True ,message='User activated',data = 'User activation successful' ,log = 'Activation successful')
            return Response(result, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            #logger.exception('Exception due to expired signature')
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            #logger.exception('Exception due to error in decoding')
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            #logger.exception('Exception due to other reasons')
            return Response({'error': 'Something went wrong'})





class RequestPasswordResetEmail(generics.GenericAPIView):
    """[sends an email to facilitate password reset]
    """
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        """[sends an email to facilitate password reset]

        Returns:
            [Response]: [message confirming link sent to email]
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
            Util.send_email(data)
            result = utils.manage_response(status=True ,data = 'We have sent you a link to reset your password' ,log = 'password link sent successfully')
        return Response(result, status=status.HTTP_200_OK)


class SetNewPassword(generics.GenericAPIView):
    """[returns new password when supplied with uid,token and new password]

    """
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        """[returns new password when supplied with uid,token and new password]

        Returns:
            [Response]: [success message after new password is set]
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.debug('password reset successful')
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


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
                logger.debug('Token validated')
                return CustomRedirect(
                    redirect_url + '?token_valid=True&message=Credentials Valid&uidb64=' + uidb64 + '&token=' + token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    logger.exception('Exception due to invalid token')
                    return CustomRedirect(redirect_url + '?token_valid=False')

            except UnboundLocalError as e:
                logger.exception('Exception due to variable being referenced before assignment')
                return Response({'error': 'Token is not valid, please request a new one'},
                                status=status.HTTP_400_BAD_REQUEST)
            except:
                logger.exception('Exception due to other reasons')
                return Response({'error': 'Something went wrong'})


