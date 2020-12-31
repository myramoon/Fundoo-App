from django.urls import path
from django.views.decorators.cache import cache_page
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.NotesOverview.as_view()),
    path('archived-notes/',views.ManageArchivedNote.as_view(),name = 'archived-notes'),
    path('manage-archived-note/<int:pk>/',views.ManageArchivedNote.as_view(),name = 'manage-specific-archived'),   
    #path('trashed-notes',views.ManageTrashedNote.as_view(),name = 'trashed-notes'),
    #path('pinned-notes',views.ManagePinnedNote.as_view(),name = 'pinned-notes'),
    path('manage-note/',views.ManageNote.as_view(),name = 'manage-notes'),
    path('manage-note/<int:pk>/',views.ManageSpecificNote.as_view(),name = 'manage-specific'),   
] 

#