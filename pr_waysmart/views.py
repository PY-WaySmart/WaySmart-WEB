from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companies.models import Empresa
from drivers.models import Repartidor
from payments.models import PagoRepartidor
from routes.models import Asignacion
from services.models import Servicio
from users.models import Perfil


@login_required
def dashboard(request):
    perfil = getattr(request.user, "perfil", None)
    rol = perfil.rol if perfil else None
    context = {
        "rol": rol,
        "perfil": perfil,
        "empresas_count": Empresa.objects.count(),
        "repartidores_count": Repartidor.objects.count(),
        "servicios_count": Servicio.objects.count(),
        "asignaciones_count": Asignacion.objects.count(),
        "pagos_count": PagoRepartidor.objects.count(),
    }

    if rol == Perfil.Rol.EMPRESA:
        context["mis_empresas"] = Empresa.objects.filter(usuario=request.user)
        mis_servicios = Servicio.objects.filter(
            empresa__usuario=request.user
        ).select_related("empresa")
        context["servicios_count"] = mis_servicios.count()
        context["mis_servicios"] = mis_servicios[:5]
        context["repartidores_count"] = Repartidor.objects.count()
        context["asignaciones_count"] = Asignacion.objects.filter(
            servicio__empresa__usuario=request.user
        ).count()
    elif rol == Perfil.Rol.REPARTIDOR:
        context["mis_repartidores"] = Repartidor.objects.filter(
            usuario=request.user
        )
        mis_asignaciones = Asignacion.objects.filter(
            repartidor__usuario=request.user
        ).select_related("servicio")
        context["mis_asignaciones"] = mis_asignaciones[:5]
        context["mis_pagos"] = PagoRepartidor.objects.filter(
            repartidor__usuario=request.user
        )[:5]
        context["asignaciones_count"] = mis_asignaciones.count()
        context["pagos_count"] = PagoRepartidor.objects.filter(
            repartidor__usuario=request.user
        ).count()
        context["repartidores_count"] = Repartidor.objects.filter(
            usuario=request.user
        ).count()

    return render(request, "dashboard.html", context)


def fn_inicio(request):
    return render(request, "pr_waysmart/bienvenido.html")