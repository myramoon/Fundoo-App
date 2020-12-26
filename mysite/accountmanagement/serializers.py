from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Account
import json


class UserDetailsSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = ['first_name','last_name','user_name','email']


class RegisterSerializer(ModelSerializer):
    """[serializer validates new user credentials and creates new user ]

    Args:
        ModelSerializer ([type]): [description]

    Raises:
        serializers.ValidationError: [description]

    Returns:
        [type]: [description]
    """
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'user_name', 'password']

    def validate(self, attrs):
        try:
            user_name = attrs.get('user_name', '')

            if not user_name.isalnum():
                raise serializers.ValidationError(
                    self.default_error_messages)
            return attrs
        except Exception:
            raise AuthenticationFailed('something went wrong', 401)

    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    #verifies email using token
    token = serializers.CharField(max_length=555)

    class Meta:
        model = Account
        fields = ['token']


class LoginSerializer(ModelSerializer):
    """[validates user credentials and allows login if authenticated]

    Args:
        ModelSerializer ([type]): [description]

    Raises:
        AuthenticationFailed: [description]
        AuthenticationFailed: [description]

    Returns:
        [type]: [description]
    """
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    user_name = serializers.CharField(
        max_length=255, min_length=3, read_only=True)

    class Meta:
        model = Account
        fields = ['email', 'password', 'user_name']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')

        return {
            #'user_name': user.user_name, 
            'email': user.email,
        }

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    """[serializes email and redirect_url when password reset request is made]

    Args:
        serializers ([type]): [description]
    """
    email = serializers.EmailField(min_length=2)
    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    """[serializes and validates uid,token,new password before new password is set for user]

    Args:
        serializers ([type]): [description]

    Raises:
        AuthenticationFailed: [description]
        AuthenticationFailed: [description]

    Returns:
        [type]: [description]
    """
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)