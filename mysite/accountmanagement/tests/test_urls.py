from django.urls import reverse, resolve


class TestUrls:
    def test_register_url(self):
        path = reverse("register")
        assert resolve(path).view_name == "register"

    def test_login_url(self):
        path = reverse("login")
        assert resolve(path).view_name == "login"

    def test_note_url(self):
        """
        this method will test url and matches result with view name as note
        """
        path = reverse("manage-notes")
        assert resolve(path).view_name == "manage-notes"

    def test_label_url(self):
        """
        this method will test url and matches result with view name as label-post
        """
        path = reverse("manage-labels")
        assert resolve(path).view_name == "manage-labels"

    def test_note_archived_url(self):
        """
        this method will test url and matches result with view name as archived
        """
        path = reverse("archived-notes")
        assert resolve(path).view_name == "archived-notes"

    def test_note_pinned_url(self):
        """
        this method will test url and matches result with view name as pinned
        """
        path = reverse("pinned-notes")
        assert resolve(path).view_name == "pinned-notes"

    def test_note_trash_url(self):
        """
        this method will test url and matches result with view name as trash
        """
        path = reverse("trashed-notes")
        assert resolve(path).view_name == "trashed-notes"

    def test_note_search_url(self):
        """
        this method will test url and matches result with view name as search
        """
        path = reverse("searched-notes")
        assert resolve(path).view_name == "searched-notes"
