from django.urls import path

from .views import HomeView, ReadinessView

app_name = "core"
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("health/ready/", ReadinessView.as_view(), name="ready"),
]
