from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import redirect, render
from django.db import transaction
from django.utils import timezone
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import LoginForm, RegistrationForm
from .models import Perfil
from companies.models import Empresa
from drivers.models import Repartidor

User = get_user_model()

MAX_INTENTOS_FALLIDOS = 5
BLOQUEO_MINUTOS = 15


class PerfilListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Perfil
    template_name = "users/list.html"
    context_object_name = "object_list"

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


def registration_view(request):
    if request.user.is_authenticated:
        return redirigir_por_rol(request.user)

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["first_name"].strip(),
                last_name=form.cleaned_data["last_name"].strip(),
                is_active=False,
            )
            perfil = user.perfil
            perfil.rol = form.cleaned_data["role"]
            perfil.estado = Perfil.Estado.PENDIENTE
            perfil.save(update_fields=["rol", "estado", "fecha_actualizacion"])
            if perfil.rol == Perfil.Rol.EMPRESA:
                Empresa.objects.create(
                    usuario=user,
                    nombre=form.cleaned_data["business_name"],
                    nit=form.cleaned_data["nit"],
                    direccion=form.cleaned_data["business_address"],
                    telefono_contacto=form.cleaned_data["business_phone"],
                    representante_legal_nombre=form.cleaned_data["legal_name"],
                    representante_legal_telefono=form.cleaned_data["legal_phone"],
                    representante_legal_correo=form.cleaned_data["legal_email"],
                    tipo_colaboracion=form.cleaned_data["tipo_colaboracion"],
                )
            else:
                Repartidor.objects.create(
                    usuario=user,
                    nombres=user.first_name,
                    apellidos=user.last_name,
                    nro_identificacion=form.cleaned_data["identification"],
                    telefono=form.cleaned_data["phone"],
                    estado="Pendiente",
                )

        messages.success(
            request,
            "Tu registro fue enviado. Un administrador debe aprobar la cuenta antes de iniciar sesión.",
        )
        return redirect("users:login")

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirigir_por_rol(request.user)

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].strip().lower()
        password = form.cleaned_data["password"]
        remember_me = form.cleaned_data.get("remember_me", False)

        user_obj = User.objects.filter(email__iexact=email).first()

        if user_obj is None:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, "users/login.html", {"form": form})

        perfil = getattr(user_obj, "perfil", None)

        if perfil and esta_bloqueado_por_intentos(perfil):
            messages.error(
                request,
                "Tu cuenta está bloqueada temporalmente por demasiados intentos fallidos. "
                "Intenta de nuevo en unos minutos.",
            )
            return render(request, "users/login.html", {"form": form})

        user = authenticate(request, username=user_obj.username, password=password)

        if user is None:
            registrar_intento_fallido(perfil)
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, "users/login.html", {"form": form})

        if not user.is_active:
            messages.error(
                request,
                "Tu cuenta está desactivada. Contacta al administrador.",
            )
            return render(request, "users/login.html", {"form": form})

        if perfil is None:
            messages.error(request, "Tu usuario no tiene un perfil asignado.")
            return render(request, "users/login.html", {"form": form})

        if perfil.estado == Perfil.Estado.BLOQUEADO:
            messages.error(
                request,
                "Tu cuenta está bloqueada. Contacta al administrador.",
            )
            return render(request, "users/login.html", {"form": form})

        if perfil.estado == Perfil.Estado.INACTIVO:
            messages.error(
                request,
                "Tu cuenta está inactiva. Contacta al administrador.",
            )
            return render(request, "users/login.html", {"form": form})

        if perfil.estado == Perfil.Estado.PENDIENTE:
            messages.error(
                request,
                "Tu cuenta aún está pendiente de aprobación. "
                "No puedes iniciar sesión todavía.",
            )
            return render(request, "users/login.html", {"form": form})

        if perfil.estado != Perfil.Estado.ACTIVO:
            messages.error(
                request,
                "Tu cuenta no puede iniciar sesión en este momento.",
            )
            return render(request, "users/login.html", {"form": form})

        limpiar_intentos_fallidos(perfil)
        login(request, user)

        if not remember_me:
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(60 * 60 * 24 * 14)

        return redirigir_por_rol(user)

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("users:login")


def redirigir_por_rol(user):
    perfil = getattr(user, "perfil", None)

    if user.is_superuser or (perfil and perfil.rol == Perfil.Rol.ADMINISTRADOR):
        return redirect("dashboard")
    if perfil and perfil.rol == Perfil.Rol.EMPRESA:
        return redirect("dashboard")
    if perfil and perfil.rol == Perfil.Rol.REPARTIDOR:
        return redirect("dashboard")

    return redirect("home")


def esta_bloqueado_por_intentos(perfil):
    if not perfil or not perfil.bloqueado_hasta:
        return False
    return perfil.bloqueado_hasta > timezone.now()


def registrar_intento_fallido(perfil):
    if not perfil:
        return
    perfil.intentos_fallidos = (perfil.intentos_fallidos or 0) + 1
    if perfil.intentos_fallidos >= MAX_INTENTOS_FALLIDOS:
        perfil.bloqueado_hasta = timezone.now() + timedelta(minutes=BLOQUEO_MINUTOS)
        perfil.intentos_fallidos = 0
    perfil.save(
        update_fields=["intentos_fallidos", "bloqueado_hasta", "fecha_actualizacion"]
    )


def limpiar_intentos_fallidos(perfil):
    if not perfil:
        return
    if perfil.intentos_fallidos or perfil.bloqueado_hasta:
        perfil.intentos_fallidos = 0
        perfil.bloqueado_hasta = None
        perfil.save(
            update_fields=["intentos_fallidos", "bloqueado_hasta", "fecha_actualizacion"]
        )