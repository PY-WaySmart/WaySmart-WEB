from django.urls import path

from .views import PerfilListView, login_view, logout_view

app_name = "users"

urlpatterns = [
    path("", PerfilListView.as_view(), name="list"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]