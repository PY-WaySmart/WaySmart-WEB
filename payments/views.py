from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import PagoRepartidor
from users.models import Perfil


class PagoRepartidorListView(LoginRequiredMixin, ListView):
    model = PagoRepartidor
    template_name = "payments/list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        queryset = PagoRepartidor.objects.select_related("repartidor", "repartidor__usuario")
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        perfil = getattr(self.request.user, "perfil", None)
        if perfil and perfil.rol == Perfil.Rol.REPARTIDOR:
            return queryset.filter(repartidor__usuario=self.request.user)
        return queryset.none()
