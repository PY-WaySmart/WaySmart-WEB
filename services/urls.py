from django.urls import path

from .views import ServicioListView, solicitud_servicio

app_name = "services"

urlpatterns = [
    path("", ServicioListView.as_view(), name="list"),
    path("nuevo/", solicitud_servicio, name="create"),
]
