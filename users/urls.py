from django.urls import path

from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from .forms import WaySmartPasswordResetForm, WaySmartSetPasswordForm
from .views import PerfilListView, login_view, logout_view, registration_view

app_name = "users"

urlpatterns = [
    path("", PerfilListView.as_view(), name="list"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("registro/", registration_view, name="register"),
    path(
        "recuperar/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
            email_template_name="users/password_reset_email.txt",
            success_url=reverse_lazy("users:password_reset_done"),
            form_class=WaySmartPasswordResetForm,
        ),
        name="password_reset",
    ),
    path(
        "recuperar/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "recuperar/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
            form_class=WaySmartSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "recuperar/completo/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]