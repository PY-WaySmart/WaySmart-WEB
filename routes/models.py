from django.db import models


class Asignacion(models.Model):
    servicio = models.ForeignKey(
        "services.Servicio",
        on_delete=models.CASCADE,
        related_name="asignaciones",
    )
    repartidor = models.ForeignKey(
        "drivers.Repartidor",
        on_delete=models.PROTECT,
        related_name="asignaciones",
    )
    fecha_aceptacion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=50)

    class Meta:
        db_table = "asignaciones"

    def __str__(self):
        return f"Asignación {self.pk}"


class Ruta(models.Model):
    asignacion = models.ForeignKey(
        Asignacion,
        on_delete=models.CASCADE,
        related_name="rutas",
        db_column="Asignaciones_asignacion_id",
    )
    tipo_ruta = models.CharField(max_length=50)
    tiempo_estimado_min = models.IntegerField()
    polyline_json = models.TextField()
    seleccionada = models.BooleanField(default=False)

    class Meta:
        db_table = "rutas"

    def __str__(self):
        return f"Ruta {self.pk}"


class SeguimientoGeolocalizacion(models.Model):
    repartidor = models.ForeignKey(
        "drivers.Repartidor",
        on_delete=models.CASCADE,
        related_name="seguimientos_geograficos",
        db_column="id_Repartidor",
    )
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    velocidad = models.IntegerField()

    def __str__(self):
        return f"Seguimiento {self.pk} - {self.repartidor}"
