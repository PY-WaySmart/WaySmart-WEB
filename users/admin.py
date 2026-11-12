from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from .models import Perfil

User = get_user_model()


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = "Perfil"
    fk_name = "usuario"
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
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

    @admin.display(description="Rol", ordering="perfil__rol")
    def get_rol(self, obj):
        if hasattr(obj, "perfil") and obj.perfil.rol:
            return obj.perfil.get_rol_display()
        return "—"

    @admin.display(description="Estado", ordering="perfil__estado")
    def get_estado(self, obj):
        if hasattr(obj, "perfil") and obj.perfil.estado:
            return obj.perfil.get_estado_display()
        return "—"


# Reemplazar el UserAdmin por defecto
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
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