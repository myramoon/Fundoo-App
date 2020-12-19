from django.urls import path
from . import views

urlpatterns = [
    path('manage-label/', views.ManageLabel.as_view()),
    path('manage-label/<int:pk>/', views.ManageSpecificLabel.as_view()),
    
] 

  