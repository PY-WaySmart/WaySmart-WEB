import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from users.models import Perfil

from .forms import (
    RegistroRepartidorForm,
    PerfilRepartidorForm,
    RegistroVehiculoForm,
    ReenviarDocumentosVehiculoForm,
)
from .models import Documento, Repartidor, Vehiculo, Modelo, Color

User = get_user_model()
logger = logging.getLogger(__name__)


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


def registro_repartidor_view(request):
    if request.user.is_authenticated:
        messages.info(request, "Ya tienes una sesión iniciada.")
        return redirect("home")

    form = RegistroRepartidorForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        archivo = data["archivo_documento"]

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=data["email"],
                    email=data["email"],
                    password=data["password"],
                    first_name=data["nombres"],
                    last_name=data["apellidos"],
                )

                perfil, _ = Perfil.objects.get_or_create(usuario=user)
                perfil.rol = Perfil.Rol.REPARTIDOR
                perfil.estado = Perfil.Estado.PENDIENTE
                perfil.save(update_fields=["rol", "estado", "fecha_actualizacion"])

                repartidor = Repartidor.objects.create(
                    usuario=user,
                    nombres=data["nombres"],
                    apellidos=data["apellidos"],
                    nro_identificacion=data["nro_identificacion"],
                    telefono=data["telefono"],
                    estado=Repartidor.Estado.PENDIENTE,
                )

                ruta = default_storage.save(
                    f"repartidores/documentos/{data['nro_identificacion']}_{archivo.name}",
                    archivo,
                )

                Documento.objects.create(
                    tipo_documento="documento_identidad",
                    url_archivo=ruta,
                    estado=Documento.Estado.VIGENTE,
                    usuario=user,
                    repartidor=repartidor,
                    entidad_tipo=Documento.EntidadTipo.REPARTIDOR,
                )

        except Exception:
            logger.exception("Error al registrar repartidor")
            messages.error(request, "No se pudo completar el registro. Intenta de nuevo.")
            return render(request, "drivers/registro.html", {"form": form})

        try:
            enviar_correo_registro(
                email=data["email"],
                nombres=data["nombres"],
                apellidos=data["apellidos"],
            )
            messages.success(
                request,
                "Registro exitoso. Tu cuenta quedó pendiente de aprobación. "
                "Revisa tu correo para la confirmación.",
            )
        except Exception:
            logger.exception("Registro guardado, pero falló el envío de correo SMTP")
            messages.warning(
                request,
                "Registro exitoso. Tu cuenta quedó pendiente de aprobación, "
                "pero no se pudo enviar el correo de confirmación.",
            )

        return redirect("drivers:registro")

    return render(request, "drivers/registro.html", {"form": form})


def enviar_correo_registro(email, nombres, apellidos):
    asunto = "WaySmart – Confirmación de registro de repartidor"
    mensaje = (
        f"Hola {nombres} {apellidos},\n\n"
        "Tu registro como repartidor en WaySmart se recibió correctamente.\n\n"
        "Estado de tu cuenta: PENDIENTE\n\n"
        "Un administrador revisará tus datos y el documento de identidad. "
        "Cuando tu cuenta sea aprobada podrás iniciar sesión y operar en la plataforma.\n\n"
        "Si no solicitaste este registro, ignora este mensaje.\n\n"
        "— Equipo WaySmart"
    )
    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


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


@login_required
def registro_vehiculo_view(request):
    perfil = getattr(request.user, "perfil", None)
    if not perfil or perfil.rol != Perfil.Rol.REPARTIDOR:
        raise PermissionDenied("Solo los repartidores pueden registrar vehículos.")

    try:
        repartidor = request.user.repartidor
    except Repartidor.DoesNotExist:
        raise PermissionDenied("No tienes un perfil de repartidor asociado.")

    form = RegistroVehiculoForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data

        try:
            with transaction.atomic():
                modelo = Modelo.objects.create(
                    marca=data["marca"],
                    nombre=data["linea"],
                    anio="",
                )
                color = Color.objects.create()

                vehiculo = Vehiculo.objects.create(
                    modelo=modelo,
                    color=color,
                    repartidor=repartidor,
                    tipo=data["tipo"],
                    marca=data["marca"],
                    linea=data["linea"],
                    placa=data["placa"],
                    estado=Vehiculo.Estado.PENDIENTE,
                    activo=False,
                )

                documentos = [
                    ("soat", data["soat"]),
                    ("licencia", data["licencia"]),
                ]

                for tipo_doc, archivo in documentos:
                    ruta = default_storage.save(
                        f"vehiculos/{vehiculo.placa}/{tipo_doc}_{archivo.name}",
                        archivo,
                    )
                    Documento.objects.create(
                        tipo_documento=tipo_doc,
                        url_archivo=ruta,
                        estado=Documento.Estado.VIGENTE,
                        usuario=request.user,
                        repartidor=repartidor,
                        vehiculo=vehiculo,
                        entidad_tipo=Documento.EntidadTipo.VEHICULO,
                    )

            messages.success(
                request,
                f"Vehículo con placa {data['placa']} registrado correctamente. "
                "Quedó pendiente de aprobación por un administrador.",
            )
            return redirect("drivers:mis_vehiculos")

        except Exception:
            logger.exception("Error al registrar vehículo")
            messages.error(request, "No se pudo registrar el vehículo. Intenta de nuevo.")

    return render(request, "drivers/registro_vehiculo.html", {"form": form})


@login_required
def mis_vehiculos_view(request):
    perfil = getattr(request.user, "perfil", None)
    if not perfil or perfil.rol != Perfil.Rol.REPARTIDOR:
        raise PermissionDenied

    try:
        repartidor = request.user.repartidor
    except Repartidor.DoesNotExist:
        raise PermissionDenied("No tienes un perfil de repartidor asociado.")

    vehiculos = (
        Vehiculo.objects.filter(repartidor=repartidor)
        .select_related("modelo")
        .order_by("-pk")
    )

    return render(
        request,
        "drivers/mis_vehiculos.html",
        {"vehiculos": vehiculos},
    )


@login_required
def reenviar_documentos_vehiculo_view(request, pk):
    perfil = getattr(request.user, "perfil", None)
    if not perfil or perfil.rol != Perfil.Rol.REPARTIDOR:
        raise PermissionDenied("Solo los repartidores pueden reenviar documentos.")

    try:
        repartidor = request.user.repartidor
    except Repartidor.DoesNotExist:
        raise PermissionDenied("No tienes un perfil de repartidor asociado.")

    vehiculo = get_object_or_404(Vehiculo, pk=pk, repartidor=repartidor)

    if vehiculo.estado != Vehiculo.Estado.RECHAZADO:
        messages.warning(
            request,
            "Solo puedes reenviar documentos de un vehículo rechazado.",
        )
        return redirect("drivers:mis_vehiculos")

    form = ReenviarDocumentosVehiculoForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data

        try:
            with transaction.atomic():
                documentos_anteriores = list(vehiculo.documentos.all())
                for doc in documentos_anteriores:
                    if doc.url_archivo and default_storage.exists(doc.url_archivo):
                        try:
                            default_storage.delete(doc.url_archivo)
                        except Exception:
                            logger.exception(
                                "No se pudo borrar archivo anterior: %s",
                                doc.url_archivo,
                            )
                    doc.delete()

                nuevos = [
                    ("soat", data["soat"]),
                    ("licencia", data["licencia"]),
                ]

                for tipo_doc, archivo in nuevos:
                    ruta = default_storage.save(
                        f"vehiculos/{vehiculo.placa}/{tipo_doc}_{archivo.name}",
                        archivo,
                    )
                    Documento.objects.create(
                        tipo_documento=tipo_doc,
                        url_archivo=ruta,
                        estado=Documento.Estado.VIGENTE,
                        usuario=request.user,
                        repartidor=repartidor,
                        vehiculo=vehiculo,
                        entidad_tipo=Documento.EntidadTipo.VEHICULO,
                    )

                vehiculo.reenviar_a_pendiente()

            messages.success(
                request,
                f"Documentos del vehículo {vehiculo.placa} actualizados. "
                "El vehículo quedó de nuevo pendiente de aprobación.",
            )
            return redirect("drivers:mis_vehiculos")

        except Exception:
            logger.exception("Error al reenviar documentos del vehículo")
            messages.error(
                request,
                "No se pudieron actualizar los documentos. Intenta de nuevo.",
            )

    return render(
        request,
        "drivers/reenviar_documentos_vehiculo.html",
        {
            "form": form,
            "vehiculo": vehiculo,
        },
    )