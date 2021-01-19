from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotesOverview.as_view()),

    path('notes/search/',views.SearchNote.as_view(),name = 'searched-notes'),

    path('notes/archived/',views.ManageArchivedNote.as_view(),name = 'archived-notes'),
    path('note/archived/<int:pk>/',views.ManageArchivedNote.as_view(),name = 'manage-specific-archived'),

    path('notes/trashed/',views.ManageTrashedNotes.as_view(),name = 'trashed-notes'),
    path('note/trashed/<int:pk>/',views.ManageTrashedNotes.as_view(),name = 'specific-trashed-note'),

    path('notes/pinned/',views.ManagePinnedNotes.as_view(),name = 'pinned-notes'),
    path('note/pinned/<int:pk>/',views.ManagePinnedNotes.as_view(),name = 'specific-pinned-note'),

    path('notes/',views.ManageNotes.as_view(),name = 'manage-notes'),
    path('note/<int:pk>/',views.ManageNotes.as_view(),name = 'manage-specific'),
]

