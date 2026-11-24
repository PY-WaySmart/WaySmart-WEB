from django import forms

from .models import Empresa


class EmpresaPerfilForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = (
            "nombre",
            "nit",
            "direccion",
            "telefono_contacto",
            "representante_legal_nombre",
            "representante_legal_telefono",
            "representante_legal_correo",
            "tipo_colaboracion",
        )
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "nit": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "direccion": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "telefono_contacto": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "representante_legal_nombre": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "representante_legal_telefono": forms.TextInput(attrs={"class": "ws-input form-control"}),
            "representante_legal_correo": forms.EmailInput(attrs={"class": "ws-input form-control"}),
            "tipo_colaboracion": forms.Select(attrs={"class": "ws-input form-select"}),
        }

    def clean_nit(self):
        nit = self.cleaned_data["nit"].strip()
        if Empresa.objects.filter(nit__iexact=nit).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe una empresa registrada con este NIT.")
        return nit
