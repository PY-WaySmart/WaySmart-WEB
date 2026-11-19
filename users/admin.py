from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import transaction
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from unfold.admin import ModelAdmin, StackedInline
from unfold.decorators import action
from unfold.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)

from .models import Perfil

User = get_user_model()


def _sync_user_access(perfil):
    user = perfil.usuario
    should_be_active = perfil.estado == Perfil.Estado.ACTIVO

    if should_be_active and (perfil.intentos_fallidos or perfil.bloqueado_hasta):
        perfil.intentos_fallidos = 0
        perfil.bloqueado_hasta = None
        perfil.save(
            update_fields=[
                "intentos_fallidos",
                "bloqueado_hasta",
                "fecha_actualizacion",
            ]
        )

    if user.is_active != should_be_active:
        user.is_active = should_be_active
        user.save(update_fields=["is_active"])


class PerfilInline(StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = "Perfil"
    fk_name = "usuario"
    extra = 0


class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    inlines = (PerfilInline,)
    actions_row = (
        "activate_user",
        "block_user",
        "inactivate_user",
    )
    readonly_fields = ("is_active",)

    list_display = (
        "username",
        "email",
        "get_rol",
        "get_estado",
        "is_staff",
        "is_active",
    )
    list_filter = ("perfil__rol", "perfil__estado", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

    def has_manage_user_status_permission(self, request):
        if request.user.is_superuser:
            return True

        perfil = getattr(request.user, "perfil", None)
        return bool(
            request.user.is_staff
            and perfil
            and perfil.rol == Perfil.Rol.ADMINISTRADOR
        )

    @admin.display(description="Rol", ordering="perfil__rol")
    def get_rol(self, obj):
        perfil = getattr(obj, "perfil", None)
        if perfil and perfil.rol:
            return perfil.get_rol_display()
        return "—"

    @admin.display(description="Estado", ordering="perfil__estado")
    def get_estado(self, obj):
        perfil = getattr(obj, "perfil", None)
        if perfil and perfil.estado:
            return perfil.get_estado_display()
        return "—"

    def save_related(self, request, form, formsets, change):
        with transaction.atomic():
            super().save_related(request, form, formsets, change)
            perfil = Perfil.objects.filter(usuario=form.instance).first()
            if perfil:
                _sync_user_access(perfil)

    def _changelist_response(self):
        changelist_url = (
            f"admin:{User._meta.app_label}_{User._meta.model_name}_changelist"
        )
        return HttpResponse(
            headers={"HX-Redirect": str(reverse_lazy(changelist_url))}
        )

    def _change_user_status(self, request, object_id, estado, label):
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])

        user = get_object_or_404(User, pk=object_id)

        try:
            perfil = user.perfil
        except Perfil.DoesNotExist:
            messages.error(request, "Este usuario no tiene un perfil asociado.")
            return self._changelist_response()

        with transaction.atomic():
            perfil.estado = estado
            perfil.save(update_fields=["estado", "fecha_actualizacion"])
            _sync_user_access(perfil)

        messages.success(request, f"Usuario actualizado: {label}.")
        return self._changelist_response()

    @action(
        description="Activar",
        permissions=["manage_user_status"],
        dialog={
            "title": "Activar usuario",
            "description": "El usuario podrá iniciar sesión.",
            "submit_text": "Activar",
        },
    )
    def activate_user(self, request, form, object_id):
        return self._change_user_status(
            request,
            object_id,
            Perfil.Estado.ACTIVO,
            "activo",
        )

    @action(
        description="Bloquear",
        permissions=["manage_user_status"],
        dialog={
            "title": "Bloquear usuario",
            "description": "El usuario ya no podrá iniciar sesión.",
            "submit_text": "Bloquear",
        },
    )
    def block_user(self, request, form, object_id):
        return self._change_user_status(
            request,
            object_id,
            Perfil.Estado.BLOQUEADO,
            "bloqueado",
        )

    @action(
        description="Inactivar",
        permissions=["manage_user_status"],
        dialog={
            "title": "Inactivar usuario",
            "description": "El usuario ya no podrá iniciar sesión.",
            "submit_text": "Inactivar",
        },
    )
    def inactivate_user(self, request, form, object_id):
        return self._change_user_status(
            request,
            object_id,
            Perfil.Estado.INACTIVO,
            "inactivo",
        )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Perfil)
class PerfilAdmin(ModelAdmin):
    list_display = (
        "usuario",
        "rol",
        "estado",
        "fecha_creacion",
        "fecha_actualizacion",
    )
    list_filter = ("rol", "estado")
    search_fields = (
        "usuario__username",
        "usuario__email",
        "usuario__first_name",
        "usuario__last_name",
    )
    readonly_fields = ("fecha_creacion", "fecha_actualizacion")
    ordering = ("-fecha_creacion",)

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            super().save_model(request, obj, form, change)
            _sync_user_access(obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions