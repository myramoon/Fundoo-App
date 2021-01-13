"""mysite URL Configuration
The `urlpatterns` list routes URLs to views.
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from __future__ import absolute_import
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accountmanagement import views


urlpatterns = [
    path('',include('labels.urls')),
    path('',include('notes.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  
    path('login/', views.Login.as_view(),name='login'),
    path('register/', views.Registration.as_view(), name ="register"),
    path('email-verify/', views.VerifyEmail.as_view(), name="email-verify"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', views.RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/',
         views.CheckPasswordToken.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', views.SetNewPassword.as_view(),
         name='password-reset-complete')

]