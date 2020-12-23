from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.NotesOverview.as_view()),
    path('manage-note/', views.ManageNote.as_view(),name='manage-notes'),
    path('manage-note/<int:pk>/',views.ManageSpecificNote.as_view(),name = 'manage-specific'),   
   # path('manage-note/', login_required(views.ManageNote.as_view()),name='manage-notes'),
    #path('manage-note/<int:pk>/', login_required(views.ManageSpecificNote.as_view()),name = 'manage-specific'),   
] 