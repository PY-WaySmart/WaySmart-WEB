from django.conf import settings
from django.db import models


class Repartidor(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="repartidor",
        null=True,
        blank=True,
    )
    nombres = models.CharField(max_length=100, null=True, blank=True)
    apellidos = models.CharField(max_length=100, null=True, blank=True)
    nro_identificacion = models.CharField(max_length=30, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)
    observacion_rechazo = models.TextField(null=True, blank=True)
    fecha_validacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return " ".join(filter(None, (self.nombres, self.apellidos))) or f"Repartidor #{self.pk}"


class Color(models.Model):
    rojo = models.PositiveIntegerField(default=0)
    amarillo = models.PositiveIntegerField(default=0)
    verde = models.PositiveIntegerField(default=0)
    negro = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["pk"]
        verbose_name = "Color"
        verbose_name_plural = "Colores"

    def __str__(self):
        return f"Color {self.pk}"


class Modelo(models.Model):
    marca = models.CharField(max_length=100, blank=True)
    nombre = models.CharField(max_length=100)
    anio = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Modelo"
        verbose_name_plural = "Modelos"

    def __str__(self):
        return f"{self.marca} {self.nombre}".strip()


class Vehiculo(models.Model):
    class Tipo(models.TextChoices):
        MOTO = "MOTO", "Moto"
        CARRO = "CARRO", "Carro"
        CAMIONETA = "CAMIONETA", "Camioneta"
        FURGON = "FURGON", "Furgón"
        OTRO = "OTRO", "Otro"

    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"
        RECHAZADO = "RECHAZADO", "Rechazado"
        PENDIENTE = "PENDIENTE", "Pendiente"

    modelo = models.ForeignKey(
        Modelo,
        on_delete=models.PROTECT,
        related_name="vehiculos",
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        related_name="vehiculos",
    )
    repartidor = models.ForeignKey(
        Repartidor,
        on_delete=models.PROTECT,
        related_name="vehiculos",
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    marca = models.CharField(max_length=100)
    linea = models.CharField(max_length=100)
    placa = models.CharField(max_length=20, unique=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    observacion_rechazo = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_validacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

    def __str__(self):
        return f"{self.placa} - {self.marca}"


class Documento(models.Model):
    class Estado(models.TextChoices):
        VIGENTE = "vigente", "Vigente"
        EXPIRADO = "expirado", "Expirado"

    class EntidadTipo(models.TextChoices):
        EMPRESA = "empresa", "Empresa"
        REPARTIDOR = "repartidor", "Repartidor"

    tipo_documento = models.CharField(max_length=100)
    url_archivo = models.CharField(max_length=200)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=Estado.choices)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documentos",
        null=True,
        blank=True,
    )
    repartidor = models.ForeignKey(
        Repartidor,
        on_delete=models.CASCADE,
        related_name="documentos",
        null=True,
        blank=True,
    )
    empresa = models.ForeignKey(
        "companies.Empresa",
        on_delete=models.CASCADE,
        related_name="documentos",
        null=True,
        blank=True,
    )
    entidad_tipo = models.CharField(max_length=50, choices=EntidadTipo.choices)

    def __str__(self):
        return self.tipo_documento
