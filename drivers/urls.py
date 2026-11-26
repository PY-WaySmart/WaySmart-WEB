from django.urls import path

from .views import RepartidorListView, editar_perfil_repartidor

app_name = "drivers"

urlpatterns = [
    path("", RepartidorListView.as_view(), name="list"),
    path("perfil/", editar_perfil_repartidor, name="profile"),
]
