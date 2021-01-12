from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotesOverview.as_view()),

    path('search-note/',views.SearchNote.as_view(),name = 'searched-notes'),

    path('archived-note/',views.ManageArchivedNote.as_view(),name = 'archived-notes'),
    path('archived-note/<int:pk>/',views.ManageArchivedNote.as_view(),name = 'manage-specific-archived'),

    path('trashed-note/',views.ManageTrashedNotes.as_view(),name = 'trashed-notes'),
    path('trashed-note/<int:pk>/',views.ManageTrashedNotes.as_view(),name = 'specific-trashed-note'),

    path('pinned-note/',views.ManagePinnedNotes.as_view(),name = 'pinned-notes'),
    path('pinned-note/<int:pk>/',views.ManagePinnedNotes.as_view(),name = 'specific-pinned-note'),

    path('manage-note/',views.ManageNotes.as_view(),name = 'manage-notes'),
    path('manage-note/<int:pk>/',views.ManageNotes.as_view(),name = 'manage-specific'),
]

