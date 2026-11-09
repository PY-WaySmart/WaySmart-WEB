from django.urls import path

from .views import PagoRepartidorListView

app_name = "payments"

urlpatterns = [
    path("", PagoRepartidorListView.as_view(), name="list"),
]
