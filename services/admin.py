from django.contrib import admin

from .models import Destino, Servicio


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("codigo_servicio", "empresa", "estado", "fecha_deseada")
    list_filter = ("estado",)
    search_fields = ("codigo_servicio", "empresa__nombre")


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = ("nombre_destinatario", "servicio", "estado_entrega", "prioridad")
    list_filter = ("estado_entrega", "prioridad")
    search_fields = ("nombre_destinatario", "direccion")
