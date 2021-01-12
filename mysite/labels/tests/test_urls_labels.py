from django.urls import reverse, resolve

class TestLabelUrls:


    def test_label_url(self):
        """
        this method will test url and matches result with view name as label-post
        """
        path = reverse("manage-labels")
        assert resolve(path).view_name == "manage-labels"

    def test_specific_label_url(self):
        """
        this method will test specific label url and matches result with view name as label-post
        """
        path = reverse("manage-specific-label",args=[1])
        assert resolve(path).view_name == "manage-specific-label"
