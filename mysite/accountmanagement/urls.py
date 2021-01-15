from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [

    path('login/', views.Login.as_view(),name='login'),
    path('logout/', views.Logout.as_view(),name='logout'),
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