from django.urls import reverse, resolve


class TestUrls:
    def test_register_url(self):
        """
         this method will test url and matches result with view name as register
        """
        path = reverse("register")
        assert resolve(path).view_name == "register"

    def test_login_url(self):
        """
        this method will test url and matches result with view name as login
        """
        path = reverse("login")
        assert resolve(path).view_name == "login"

