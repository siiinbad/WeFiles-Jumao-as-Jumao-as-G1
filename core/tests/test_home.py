from django.conf import settings
from django.test import SimpleTestCase, override_settings
from django.urls import reverse


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    STORAGES={"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}},
    MIDDLEWARE=[
        item for item in settings.MIDDLEWARE if item != "whitenoise.middleware.WhiteNoiseMiddleware"
    ],
)
class HomeTests(SimpleTestCase):
    def test_landing_page_uses_shared_template_without_database_queries(self):
        response = self.client.get(reverse("core:home"), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "core/home.html")
        self.assertContains(response, "Skip to content")
        self.assertContains(response, "/static/css/app.css")
        self.assertContains(response, '<h1 id="welcome-title">')

    def test_browser_security_headers_are_present(self):
        response = self.client.get(reverse("core:home"), secure=True)
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
