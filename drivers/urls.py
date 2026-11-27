from django.urls import path

from .views import (
    RepartidorListView,
    registro_repartidor_view,
    editar_perfil_repartidor,
    registro_vehiculo_view,
)

app_name = "drivers"

urlpatterns = [
    path("", RepartidorListView.as_view(), name="list"),
    path("perfil/", editar_perfil_repartidor, name="profile"),
    path("vehiculo/registro/", registro_vehiculo_view, name="registro_vehiculo"),
]   