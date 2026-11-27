from django.urls import path

from .views import (
    RepartidorListView,
    registro_repartidor_view,
    editar_perfil_repartidor,
    registro_vehiculo_view,
    mis_vehiculos_view,
    reenviar_documentos_vehiculo_view,
)

app_name = "drivers"

urlpatterns = [
    path("", RepartidorListView.as_view(), name="list"),
    path("registro/", registro_repartidor_view, name="registro"),
    path("perfil/", editar_perfil_repartidor, name="profile"),
    path("vehiculo/registro/", registro_vehiculo_view, name="registro_vehiculo"),
    path("vehiculos/", mis_vehiculos_view, name="mis_vehiculos"),
    path(
        "vehiculos/<int:pk>/reenviar-documentos/",
        reenviar_documentos_vehiculo_view,
        name="reenviar_documentos",
    ),
]