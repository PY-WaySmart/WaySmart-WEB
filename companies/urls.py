from django.urls import path

from .views import EmpresaListView

app_name = "companies"

urlpatterns = [
    path("", EmpresaListView.as_view(), name="list"),
]
