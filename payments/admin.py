from django.contrib import admin

from .models import PagoEntrega, PagoRepartidor, TipoDePago


@admin.register(PagoEntrega)
class PagoEntregaAdmin(admin.ModelAdmin):
    list_display = ("valor_total", "metodo_pago", "fecha_de_pago", "estado")
    list_filter = ("estado", "metodo_pago")


@admin.register(PagoRepartidor)
class PagoRepartidorAdmin(admin.ModelAdmin):
    list_display = ("repartidor", "monto_neto", "fecha_pago", "estado")
    list_filter = ("estado",)


admin.site.register(TipoDePago)
