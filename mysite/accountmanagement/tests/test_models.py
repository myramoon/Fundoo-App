import pytest
from mixer.backend.django import mixer
pytestmark = pytest.mark.django_db

class TestNote:
    def test_init(self):
        user_obj = mixer.blend('accountmanagement.Account')
        assert user_obj.pk == 1