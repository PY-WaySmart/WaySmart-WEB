from django.db import models


class Servicio(models.Model):
    class Estado(models.TextChoices):
        SOLICITADO = "Solicitado", "Solicitado"
        EN_PROCESO = "En Proceso", "En Proceso"
        COMPLETADO = "Completado", "Completado"
        CANCELADO = "Cancelado", "Cancelado"

    empresa = models.ForeignKey(
        "companies.Empresa",
        on_delete=models.PROTECT,
        related_name="servicios",
    )
    codigo_servicio = models.CharField(max_length=50)
    tipo_envio = models.CharField(max_length=100, blank=True)
    cantidad_entregas = models.PositiveIntegerField(null=True, blank=True)
    direccion_recogidas = models.CharField(max_length=500)
    fecha_deseada = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.SOLICITADO,
    )
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return self.codigo_servicio


class Destino(models.Model):
    class Prioridad(models.TextChoices):
        BAJA = "Baja", "Baja"
        MEDIA = "Media", "Media"
        ALTA = "Alta", "Alta"

    class EstadoEntrega(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        EN_RUTA = "En Ruta", "En Ruta"
        ENTREGADO = "Entregado", "Entregado"
        CANCELADO = "Cancelado", "Cancelado"

    pago_entrega = models.ForeignKey(
        "payments.PagoEntrega",
        on_delete=models.SET_NULL,
        related_name="destinos",
        null=True,
        blank=True,
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name="destinos",
        null=True,
        blank=True,
    )
    asignacion = models.ForeignKey(
        "routes.Asignacion",
        on_delete=models.SET_NULL,
        related_name="destinos",
        null=True,
        blank=True,
    )
    nombre_destinatario = models.CharField(max_length=150)
    telefono_destinatario = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=500)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    prioridad = models.CharField(
        max_length=10,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
    )
    estado_entrega = models.CharField(
        max_length=20,
        choices=EstadoEntrega.choices,
        default=EstadoEntrega.PENDIENTE,
    )
    firma_digital_url = models.URLField(max_length=500, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return self.nombre_destinatario
