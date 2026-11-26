from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from users.models import Perfil
from .forms import AsignarServicioForm
from .models import Asignacion
from services.models import Servicio


class RutaListView(LoginRequiredMixin, ListView):
    model = Asignacion
    template_name = "routes/list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        queryset = Asignacion.objects.select_related(
            "servicio__empresa",
            "repartidor__usuario",
        ).prefetch_related("rutas")
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        perfil = getattr(self.request.user, "perfil", None)
        if perfil and perfil.rol == Perfil.Rol.REPARTIDOR:
            return queryset.filter(repartidor__usuario=self.request.user)
        if perfil and perfil.rol == Perfil.Rol.EMPRESA:
            return queryset.filter(servicio__empresa__usuario=self.request.user)
        return queryset.none()


@login_required
def asignar_servicio(request):
    if not request.user.is_staff and not request.user.is_superuser:
        raise PermissionDenied
    form = AsignarServicioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        asignacion = form.save(commit=False)
        asignacion.estado = "Pendiente"
        asignacion.save()
        messages.success(request, "El servicio fue asignado al repartidor.")
        return redirect("routes:list")
    return render(request, "routes/assign.html", {"form": form})


@login_required
@require_POST
def actualizar_asignacion(request, pk):
    with transaction.atomic():
        asignacion = get_object_or_404(
            Asignacion.objects.select_for_update().select_related(
                "repartidor__usuario",
                "servicio",
            ),
            pk=pk,
        )
        if not request.user.is_staff and asignacion.repartidor.usuario_id != request.user.id:
            raise PermissionDenied

        nuevo_estado = request.POST.get("estado")
        estado_actual = (asignacion.estado or "").strip().casefold()
        if (
            nuevo_estado == "Aceptada"
            and estado_actual in {"pendiente", "asignada", "pendiente de aceptación", ""}
            and asignacion.servicio.estado != Servicio.Estado.CANCELADO
        ):
            asignacion.estado = "Aceptada"
            asignacion.fecha_aceptacion = timezone.now()
            asignacion.save(update_fields=["estado", "fecha_aceptacion"])
            Servicio.objects.filter(pk=asignacion.servicio_id).update(
                estado=Servicio.Estado.EN_PROCESO
            )
            messages.success(request, "Aceptaste el servicio asignado.")
        elif nuevo_estado == "Completada" and estado_actual in {"aceptada", "en curso"}:
            asignacion.estado = "Completada"
            asignacion.save(update_fields=["estado"])
            quedan_pendientes = Asignacion.objects.filter(
                servicio_id=asignacion.servicio_id
            ).exclude(estado__iexact="Completada").exists()
            if not quedan_pendientes:
                Servicio.objects.filter(pk=asignacion.servicio_id).update(
                    estado=Servicio.Estado.COMPLETADO
                )
            messages.success(request, "El servicio quedó marcado como completado.")
        else:
            messages.error(request, "No se puede aplicar ese cambio al estado actual.")
    return redirect("routes:list")
