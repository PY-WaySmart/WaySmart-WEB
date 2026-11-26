from django import forms

from .models import Repartidor


class PerfilRepartidorForm(forms.ModelForm):
    class Meta:
        model = Repartidor
        fields = ("nombres", "apellidos", "nro_identificacion", "telefono")
        widgets = {
            "nombres": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "apellidos": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "nro_identificacion": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "telefono": forms.TextInput(attrs={"class": "ws-input form-control"}),
        }
