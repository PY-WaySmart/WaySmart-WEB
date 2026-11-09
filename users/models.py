from django.conf import settings
from django.db import models


class Perfil(models.Model):
    class Rol(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"
        REPARTIDOR = "repartidor", "Repartidor"
        EMPRESA = "empresa", "Empresa"

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    rol = models.CharField(max_length=20, choices=Rol.choices)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario} ({self.get_rol_display()})"
