from django.urls import reverse,resolve

class TestNoteUrls:

    def test_note_url(self):
        """
        this method will test url and matches result with view name as note
        """
        path = reverse("manage-notes")
        assert resolve(path).view_name == "manage-notes"

    def test_specific_note_url(self):
        """
        this method will test url and matches result with view name as note
        """
        path = reverse("manage-specific",args=[1])
        assert resolve(path).view_name == "manage-specific"


    def test_note_archived_url(self):
        """
        this method will test url and matches result with view name as archived
        """
        path = reverse("archived-notes")
        assert resolve(path).view_name == "archived-notes"


    def test_specific_archived_note_url(self):
        """
        this method will test url and matches result with view name as archived
        """
        path = reverse("manage-specific-archived", args=[1])
        assert resolve(path).view_name == "manage-specific-archived"


    def test_note_pinned_url(self):
        """
        this method will test url and matches result with view name as pinned
        """
        path = reverse("pinned-notes")
        assert resolve(path).view_name == "pinned-notes"


    def test_specific_pinned_note_url(self):
        """
        this method will test url and matches result with view name as archived
        """
        path = reverse("specific-pinned-note", args=[1])
        assert resolve(path).view_name == "specific-pinned-note"


    def test_note_trash_url(self):
        """
        this method will test url and matches result with view name as trash
        """
        path = reverse("trashed-notes")
        assert resolve(path).view_name == "trashed-notes"


    def test_specific_trashed_note_url(self):
        """
        this method will test url and matches result with view name as archived
        """
        path = reverse("specific-trashed-note", args=[1])
        assert resolve(path).view_name == "specific-trashed-note"


    def test_note_search_url(self):
        """
        this method will test url and matches result with view name as search
        """
        path = reverse("searched-notes")
        assert resolve(path).view_name == "searched-notes"
