from django.conf import settings
from django.db import models


class Empresa(models.Model):
    class TipoColaboracion(models.TextChoices):
        SOCIO = "SOCIO", "Socio Comercial"
        PROVEEDOR = "PROVEEDOR", "Proveedor"
        ALIADO = "ALIADO", "Aliado Estratégico"

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="empresas",
    )
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=50, unique=True)
    direccion = models.CharField(max_length=300)
    telefono_contacto = models.CharField(max_length=20)
    representante_legal_nombre = models.CharField(max_length=200)
    representante_legal_telefono = models.CharField(max_length=20)
    representante_legal_correo = models.EmailField(max_length=225)
    tipo_colaboracion = models.CharField(
        max_length=50,
        choices=TipoColaboracion.choices,
    )
    estado = models.CharField(
        max_length=50,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    observacion_rechazo = models.TextField(blank=True, null=True)
    fecha_validacion = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Convenio(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"
        FINALIZADO = "FINALIZADO", "Finalizado"

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="convenios",
    )
    porcentaje_comision = models.DecimalField(max_digits=5, decimal_places=2)
    zonas_cobertura = models.TextField()
    condiciones_facturacion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    estado = models.CharField(
        max_length=50,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )

    def __str__(self):
        return f"Convenio #{self.pk} - {self.empresa.nombre}"
