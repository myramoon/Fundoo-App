import pytest
from mixer.backend.django import mixer
pytestmark = pytest.mark.django_db

class TestNotes:
    def test_init(self):
        note_obj = mixer.blend('notes.Note', title='Sample Note', description='Sample description')
        assert note_obj.pk == 1
        assert note_obj.title == 'Sample Note'

    def test_note_is_soft_deleted(self):
        note_obj = mixer.blend('notes.Note',is_trashed = False)
        note_obj.soft_delete()
        assert note_obj.is_trashed == True