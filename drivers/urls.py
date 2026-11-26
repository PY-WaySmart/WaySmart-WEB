from django.urls import path

from .views import RepartidorListView, registro_repartidor_view, editar_perfil_repartidor

app_name = "drivers"

urlpatterns = [
    path("", RepartidorListView.as_view(), name="list"),
    path("registro/", registro_repartidor_view, name="registro"),
    path("perfil/", editar_perfil_repartidor, name="profile"),
]