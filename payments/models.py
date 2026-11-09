from django.db import models


class TipoDePago(models.Model):
    efectivo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    transferencia = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Tipo de pago #{self.pk}"


class PagoEntrega(models.Model):
    class Metodo(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"
        OTRO = "OTRO", "Otro"

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        COMPLETADO = "COMPLETADO", "Completado"
        CANCELADO = "CANCELADO", "Cancelado"

    tipo_de_pago = models.ForeignKey(
        TipoDePago,
        on_delete=models.PROTECT,
        related_name="pagos_entrega",
    )
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, choices=Metodo.choices)
    evidencia_url = models.CharField(max_length=255, null=True, blank=True)
    fecha_de_pago = models.DateTimeField()
    estado = models.CharField(max_length=50, choices=Estado.choices, default=Estado.PENDIENTE)

    def __str__(self):
        return f"Pago de entrega #{self.pk} - {self.estado}"


class PagoRepartidor(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PAGADO = "pagado", "Pagado"
        FALLIDO = "fallido", "Fallido"

    repartidor = models.ForeignKey(
        "drivers.Repartidor",
        on_delete=models.PROTECT,
        related_name="pagos",
        db_column="id_Repartidor",
    )
    monto_total_generado = models.DecimalField(max_digits=12, decimal_places=2)
    comision_plataforma = models.DecimalField(max_digits=12, decimal_places=2)
    monto_neto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)

    def __str__(self):
        return f"Pago al repartidor #{self.pk} - {self.estado}"
