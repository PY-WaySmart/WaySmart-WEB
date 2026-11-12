from django.urls import path

from .views import RutaListView

app_name = "routes"

urlpatterns = [
    path("", RutaListView.as_view(), name="list"),
]
