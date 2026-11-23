from django.urls import path

from .views import RepartidorListView, registro_repartidor_view

app_name = "drivers"

urlpatterns = [
    path("", RepartidorListView.as_view(), name="list"),
    path("registro/", registro_repartidor_view, name="registro"),
]