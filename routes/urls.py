from django.urls import path

from .views import RutaListView, actualizar_asignacion, asignar_servicio

app_name = "routes"

urlpatterns = [
    path("", RutaListView.as_view(), name="list"),
    path("asignar/", asignar_servicio, name="assign"),
    path("asignaciones/<int:pk>/estado/", actualizar_asignacion, name="update_assignment"),
]
