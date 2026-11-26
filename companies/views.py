from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import EmpresaPerfilForm
from .models import Empresa
from users.models import Perfil


class EmpresaListView(LoginRequiredMixin, ListView):
    model = Empresa
    template_name = "companies/list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        queryset = Empresa.objects.select_related("usuario")
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        perfil = getattr(self.request.user, "perfil", None)
        if perfil and perfil.rol == Perfil.Rol.EMPRESA:
            return queryset.filter(usuario=self.request.user)
        return queryset.none()


@login_required
def editar_perfil_empresa(request):
    perfil = getattr(request.user, "perfil", None)
    if not perfil or perfil.rol != Perfil.Rol.EMPRESA:
        raise PermissionDenied
    empresa = get_object_or_404(Empresa, usuario=request.user)
    form = EmpresaPerfilForm(request.POST or None, instance=empresa)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Los datos de tu empresa fueron actualizados.")
        return redirect("companies:list")
    return render(request, "companies/profile_form.html", {"form": form})
