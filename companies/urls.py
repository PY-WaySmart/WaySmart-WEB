from django.urls import path

from .views import EmpresaListView, editar_perfil_empresa

app_name = "companies"

urlpatterns = [
    path("", EmpresaListView.as_view(), name="list"),
    path("perfil/", editar_perfil_empresa, name="profile"),
]
