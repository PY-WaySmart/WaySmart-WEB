from django.urls import path

from .views import PerfilListView

app_name = "users"

urlpatterns = [
    path("", PerfilListView.as_view(), name="list"),
]
