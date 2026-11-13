import logging

from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "core/home.html"


class ReadinessView(View):
    http_method_names = ["get", "head", "options"]

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except DatabaseError:
            # Connection exception text can contain private infrastructure details.
            logger.warning("Database readiness check failed")
            response = JsonResponse({"status": "unavailable"}, status=503)
        else:
            response = JsonResponse({"status": "ready"})
        response["Cache-Control"] = "no-store"
        return response
