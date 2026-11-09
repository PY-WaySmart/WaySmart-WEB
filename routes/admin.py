from django.contrib import admin

from .models import Asignacion, Ruta, SeguimientoGeolocalizacion


@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ("servicio", "repartidor", "estado", "fecha_aceptacion")
    list_filter = ("estado",)


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ("asignacion", "tipo_ruta", "tiempo_estimado_min", "seleccionada")
    list_filter = ("seleccionada",)


admin.site.register(SeguimientoGeolocalizacion)
