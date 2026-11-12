from django.conf import settings
from django.db import models


class Perfil(models.Model):
    class Rol(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"
        EMPRESA = "empresa", "Empresa"
        REPARTIDOR = "repartidor", "Repartidor"

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        PENDIENTE = "pendiente", "Pendiente"
        BLOQUEADO = "bloqueado", "Bloqueado"
        INACTIVO = "inactivo", "Inactivo"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        # Obligatorio: sin blank=True ni null=True
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.usuario} ({self.get_rol_display()})"