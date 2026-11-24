from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.generic import ListView

from companies.models import Empresa
from users.models import Perfil

from .forms import DestinoSolicitudFormSet, SolicitudServicioForm
from .models import Destino
from .models import Servicio


class ServicioListView(LoginRequiredMixin, ListView):
    model = Servicio
    template_name = "services/list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        queryset = Servicio.objects.select_related("empresa").prefetch_related("destinos")
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        perfil = getattr(self.request.user, "perfil", None)
        if perfil and perfil.rol == Perfil.Rol.EMPRESA:
            return queryset.filter(empresa__usuario=self.request.user)
        if perfil and perfil.rol == Perfil.Rol.REPARTIDOR:
            return queryset.filter(
                asignaciones__repartidor__usuario=self.request.user
            ).distinct()
        return queryset.none()


@login_required
def solicitud_servicio(request):
    perfil = getattr(request.user, "perfil", None)
    if not perfil or perfil.rol != Perfil.Rol.EMPRESA:
        raise PermissionDenied

    empresa = Empresa.objects.filter(usuario=request.user).first()
    if empresa is None:
        messages.error(request, "No encontramos una empresa asociada a tu cuenta.")
        return redirect("dashboard")
    if empresa.estado != Empresa.Estado.APROBADO:
        messages.warning(
            request,
            "Tu empresa debe ser aprobada por un administrador antes de solicitar servicios.",
        )
        return redirect("dashboard")

    form = SolicitudServicioForm(request.POST or None)
    destinos = DestinoSolicitudFormSet(request.POST or None, prefix="destinos")
    if request.method == "POST" and form.is_valid() and destinos.is_valid():
        with transaction.atomic():
            servicio = form.save(commit=False)
            servicio.empresa = empresa
            servicio.cantidad_entregas = sum(
                1 for destino_form in destinos if destino_form.has_changed()
            )
            servicio.save()
            Destino.objects.bulk_create(
                [
                    Destino(
                        servicio=servicio,
                        nombre_destinatario=destino_form.cleaned_data["nombre_destinatario"],
                        telefono_destinatario=destino_form.cleaned_data["telefono_destinatario"],
                        direccion=destino_form.cleaned_data["direccion_destino"],
                        prioridad=destino_form.cleaned_data["prioridad"],
                    )
                    for destino_form in destinos
                    if destino_form.has_changed()
                ]
            )
        messages.success(request, "La solicitud de servicio fue creada correctamente.")
        return redirect("services:list")

    return render(
        request,
        "services/create.html",
        {"form": form, "destinos": destinos},
    )
