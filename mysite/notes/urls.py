from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotesOverview.as_view()),
    path('manage-note/', views.ManageNote.as_view()),
    path('manage-note/<int:pk>/', views.ManageSpecificNote.as_view()),   
] 