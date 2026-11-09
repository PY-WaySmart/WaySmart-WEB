from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("usuarios/", include("users.urls")),
    path("empresas/", include("companies.urls")),
    path("repartidores/", include("drivers.urls")),
    path("servicios/", include("services.urls")),
    path("rutas/", include("routes.urls")),
    path("pagos/", include("payments.urls")),
]
