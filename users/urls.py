from django.urls import path
from .views import PerfilListView, login_view

app_name = "users"

urlpatterns = [
    path("", PerfilListView.as_view(), name="list"),
    path("login/", login_view, name="login"),
]