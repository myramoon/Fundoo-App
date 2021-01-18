from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotesOverview.as_view()),

    path('search-notes/',views.SearchNote.as_view(),name = 'searched-notes'),

    path('archived-notes/',views.ManageArchivedNote.as_view(),name = 'archived-notes'),
    path('archived-note/<int:pk>/',views.ManageArchivedNote.as_view(),name = 'manage-specific-archived'),

    path('trashed-notes/',views.ManageTrashedNotes.as_view(),name = 'trashed-notes'),
    path('trashed-note/<int:pk>/',views.ManageTrashedNotes.as_view(),name = 'specific-trashed-note'),

    path('pinned-notes/',views.ManagePinnedNotes.as_view(),name = 'pinned-notes'),
    path('pinned-note/<int:pk>/',views.ManagePinnedNotes.as_view(),name = 'specific-pinned-note'),

    path('notes/',views.ManageNotes.as_view(),name = 'manage-notes'),
    path('note/<int:pk>/',views.ManageNotes.as_view(),name = 'manage-specific'),
]

