from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import PerfilRepartidorForm
from .models import Repartidor
from users.models import Perfil


class RepartidorListView(LoginRequiredMixin, ListView):
    model = Repartidor
    template_name = "drivers/list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        queryset = Repartidor.objects.select_related("usuario")
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        perfil = getattr(self.request.user, "perfil", None)
        if perfil and perfil.rol == Perfil.Rol.REPARTIDOR:
            return queryset.filter(usuario=self.request.user)
        return queryset.none()


@login_required
def editar_perfil_repartidor(request):
    perfil = getattr(request.user, "perfil", None)
    if not perfil or perfil.rol != Perfil.Rol.REPARTIDOR:
        raise PermissionDenied
    repartidor = get_object_or_404(Repartidor, usuario=request.user)
    form = PerfilRepartidorForm(request.POST or None, instance=repartidor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Los datos de tu perfil fueron actualizados.")
        return redirect("drivers:list")
    return render(request, "drivers/profile_form.html", {"form": form})
