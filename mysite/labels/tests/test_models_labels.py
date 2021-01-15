import pytest
from mixer.backend.django import mixer
pytestmark = pytest.mark.django_db

class TestLabels:
    def test_init(self):
        label_obj = mixer.blend('labels.Label', name='Label1')
        assert label_obj.pk == 1
        assert label_obj.name == 'Label1'

