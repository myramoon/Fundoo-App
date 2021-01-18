from django.urls import path
from . import views

urlpatterns = [
    path('labels/', views.ManageLabel.as_view(),name = 'manage-labels'),
    path('label/<int:pk>/', views.ManageLabel.as_view(),name='manage-specific-label'),
    
] 

  