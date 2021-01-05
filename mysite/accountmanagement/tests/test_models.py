import pytest
from mixer.backend.django import mixer
pytestmark = pytest.mark.django_db

class TestNote:
    def test_init(self):
        user_obj = mixer.blend('accountmanagement.Account', first_name='Asdfg')
        assert user_obj.pk == 1
        assert user_obj.first_name == 'Asdfg'