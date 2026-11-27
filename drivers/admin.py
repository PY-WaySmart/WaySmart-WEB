from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import Color, Documento, Modelo, Repartidor, Vehiculo


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    can_delete = False
    readonly_fields = ("tipo_documento", "enlace_archivo", "estado", "fecha_subida")
    fields = ("tipo_documento", "enlace_archivo", "estado", "fecha_subida")

    def enlace_archivo(self, obj):
        if not obj.url_archivo:
            return "—"
        return format_html(
            '<a href="/media/{}" target="_blank" rel="noopener">Ver documento</a>',
            obj.url_archivo,
        )

    enlace_archivo.short_description = "Archivo"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Vehiculo)
class VehiculoAdmin(ModelAdmin):
    list_display = (
        "placa",
        "marca",
        "tipo",
        "repartidor",
        "estado",
        "activo",
        "alerta_documentos",
        "fecha_validacion",
    )
    list_filter = ("estado", "tipo", "activo")
    search_fields = (
        "placa",
        "marca",
        "repartidor__nombres",
        "repartidor__apellidos",
        "repartidor__nro_identificacion",
    )
    readonly_fields = ("fecha_validacion", "alerta_documentos_detalle")
    inlines = [DocumentoInline]
    actions_row = (
        "aprobar_vehiculo",
        "ir_a_rechazar",
    )

    fieldsets = (
        (
            "Datos del vehículo",
            {
                "fields": (
                    "placa",
                    "tipo",
                    "marca",
                    "linea",
                    "modelo",
                    "color",
                    "repartidor",
                )
            },
        ),
        (
            "Validación",
            {
                "fields": (
                    "estado",
                    "activo",
                    "observacion_rechazo",
                    "fecha_validacion",
                    "alerta_documentos_detalle",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("repartidor", "modelo")
            .prefetch_related("documentos")
        )

    @admin.display(description="Documentos")
    def alerta_documentos(self, obj):
        if obj.tiene_documentos_expirados():
            return format_html(
                '<span style="color:#c0392b;font-weight:bold;">{}</span>',
                "⚠ Vencidos",
            )
        return format_html(
            '<span style="color:#27ae60;">{}</span>',
            "OK",
        )

    @admin.display(description="Alerta de documentos")
    def alerta_documentos_detalle(self, obj):
        expirados = list(obj.documentos_expirados())
        if not expirados:
            return "Todos los documentos están vigentes."
        nombres = ", ".join(d.tipo_documento for d in expirados)
        return format_html(
            '<span style="color:#c0392b;font-weight:bold;">Documentos vencidos: {}</span>',
            nombres,
        )

    def has_manage_vehiculo_permission(self, request):
        if request.user.is_superuser:
            return True
        perfil = getattr(request.user, "perfil", None)
        return bool(
            request.user.is_staff
            and perfil
            and getattr(perfil, "rol", None) == "ADMINISTRADOR"
        )

    @action(
        description="Aprobar",
        permissions=["manage_vehiculo"],
        dialog={
            "title": "Aprobar vehículo",
            "description": (
                "El vehículo pasará a estado ACTIVO y será el único "
                "vehículo activo del repartidor. ¿Continuar?"
            ),
            "submit_text": "Aprobar",
        },
    )
    def aprobar_vehiculo(self, request, form, object_id):
        try:
            vehiculo = Vehiculo.objects.get(pk=object_id)
        except Vehiculo.DoesNotExist:
            messages.error(request, "Vehículo no encontrado.")
            return

        if vehiculo.estado != Vehiculo.Estado.PENDIENTE:
            messages.warning(
                request,
                f"El vehículo {vehiculo.placa} no está en estado PENDIENTE.",
            )
            return

        if vehiculo.tiene_documentos_expirados():
            messages.warning(
                request,
                f"El vehículo {vehiculo.placa} tiene documentos vencidos. "
                "Revise antes de aprobar.",
            )

        try:
            vehiculo.aprobar()
            messages.success(
                request,
                f"Vehículo {vehiculo.placa} aprobado y marcado como activo.",
            )
        except Exception as exc:
            messages.error(request, f"No se pudo aprobar: {exc}")

    @action(
        description="Rechazar",
        permissions=["manage_vehiculo"],
    )
    def ir_a_rechazar(self, request, form, object_id):
        url = reverse("admin:drivers_vehiculo_change", args=[object_id])
        messages.info(
            request,
            "Indique el motivo de rechazo en el campo «Observación de rechazo», "
            "cambie el estado a RECHAZADO y guarde.",
        )
        return HttpResponseRedirect(url)

    def save_model(self, request, obj, form, change):
        # Validar motivo obligatorio al rechazar
        if obj.estado == Vehiculo.Estado.RECHAZADO:
            if not obj.observacion_rechazo or not obj.observacion_rechazo.strip():
                messages.error(
                    request,
                    "Debes indicar el motivo de rechazo en el campo "
                    "«Observación de rechazo».",
                )
                return

            try:
                obj.rechazar(obj.observacion_rechazo)
                messages.success(
                    request,
                    f"Vehículo {obj.placa} rechazado correctamente.",
                )
                return
            except ValueError as exc:
                messages.error(request, str(exc))
                return

        # Si se marca como ACTIVO desde el formulario, usar la lógica de aprobar
        if obj.estado == Vehiculo.Estado.ACTIVO and obj.activo:
            try:
                obj.aprobar()
                messages.success(
                    request,
                    f"Vehículo {obj.placa} aprobado correctamente.",
                )
                return
            except Exception as exc:
                messages.error(request, f"No se pudo aprobar: {exc}")
                return

        super().save_model(request, obj, form, change)


@admin.register(Repartidor)
class RepartidorAdmin(ModelAdmin):
    list_display = ("nombres", "apellidos", "nro_identificacion", "telefono", "estado")
    list_filter = ("estado",)
    search_fields = ("nombres", "apellidos", "nro_identificacion")


admin.site.register((Color, Modelo, Documento))