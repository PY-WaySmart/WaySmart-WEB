from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Asignacion, Ruta, SeguimientoGeolocalizacion


@admin.register(Asignacion)
class AsignacionAdmin(ModelAdmin):
    list_display = ("servicio", "repartidor", "estado", "fecha_aceptacion")
    list_filter = ("estado",)


@admin.register(Ruta)
class RutaAdmin(ModelAdmin):
    list_display = ("asignacion", "tipo_ruta", "tiempo_estimado_min", "seleccionada")
    list_filter = ("seleccionada",)


admin.site.register(SeguimientoGeolocalizacion)

