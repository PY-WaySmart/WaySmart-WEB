import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.generic import ListView

from users.models import Perfil

from .forms import RegistroRepartidorForm
from .models import Documento, Repartidor

User = get_user_model()
logger = logging.getLogger(__name__)


class RepartidorListView(ListView):
    model = Repartidor
    template_name = "drivers/list.html"
    context_object_name = "object_list"


def registro_repartidor_view(request):
    """
    Registro de repartidor.
    Crea User + Perfil (REPARTIDOR, PENDIENTE) + Repartidor (PENDIENTE)
    + Documento (PDF). Envía correo con el estado de la cuenta.
    """
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
            messages.error(
                request,
                "No se pudo completar el registro. Intenta de nuevo.",
            )
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
    """
    Envía correo de confirmación indicando que la cuenta quedó en estado PENDIENTE.
    Si no hay EMAIL_HOST_PASSWORD en el .env local, se imprime en la terminal.
    """
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