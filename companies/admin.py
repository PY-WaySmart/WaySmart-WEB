from django.contrib import admin

from .models import Convenio, Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit", "usuario", "estado")
    list_filter = ("estado", "tipo_colaboracion")
    search_fields = ("nombre", "nit", "usuario__username")


@admin.register(Convenio)
class ConvenioAdmin(admin.ModelAdmin):
    list_display = ("empresa", "porcentaje_comision", "fecha_inicio", "fecha_termino", "estado")
    list_filter = ("estado",)
