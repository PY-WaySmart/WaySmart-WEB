from django.contrib import admin

from .models import Color, Documento, Modelo, Repartidor, Vehiculo


@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    list_display = ("nombres", "apellidos", "nro_identificacion", "telefono", "estado")
    list_filter = ("estado",)
    search_fields = ("nombres", "apellidos", "nro_identificacion")


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "marca", "modelo", "repartidor", "estado")
    list_filter = ("estado", "tipo", "activo")
    search_fields = ("placa", "marca", "repartidor__nombres", "repartidor__apellidos")


admin.site.register((Color, Modelo, Documento))
