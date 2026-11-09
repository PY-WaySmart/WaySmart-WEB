from django.urls import path

from .views import ServicioListView

app_name = "services"

urlpatterns = [
    path("", ServicioListView.as_view(), name="list"),
]
