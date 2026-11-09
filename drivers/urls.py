from django.urls import path

from .views import RepartidorListView

app_name = "drivers"

urlpatterns = [
    path("", RepartidorListView.as_view(), name="list"),
]
