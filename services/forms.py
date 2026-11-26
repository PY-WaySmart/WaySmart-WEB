from django import forms
from django.forms import formset_factory

from .models import Destino, Servicio


class DestinoSolicitudForm(forms.Form):
    nombre_destinatario = forms.CharField(
        label="Nombre del destinatario",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "ws-input form-control"}),
    )
    telefono_destinatario = forms.CharField(
        label="Teléfono del destinatario",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "ws-input form-control"}),
    )
    direccion_destino = forms.CharField(
        label="Dirección de entrega",
        max_length=500,
        widget=forms.TextInput(attrs={"class": "ws-input form-control"}),
    )
    prioridad = forms.ChoiceField(
        label="Prioridad",
        choices=Destino.Prioridad.choices,
        widget=forms.Select(attrs={"class": "ws-input form-select"}),
    )


DestinoSolicitudFormSet = formset_factory(
    DestinoSolicitudForm,
    extra=1,
    min_num=1,
    validate_min=True,
    max_num=20,
    validate_max=True,
)


class SolicitudServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = (
            "codigo_servicio",
            "tipo_envio",
            "cantidad_entregas",
            "direccion_recogidas",
            "fecha_deseada",
            "observaciones",
        )
        widgets = {
            "codigo_servicio": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "tipo_envio": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "cantidad_entregas": forms.NumberInput(attrs={"class": "ws-input form-control", "min": "1"}),
            "direccion_recogidas": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "fecha_deseada": forms.DateTimeInput(
                attrs={"class": "ws-input form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "observaciones": forms.Textarea(attrs={"class": "ws-input form-control", "rows": 3}),
        }
