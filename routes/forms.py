from django import forms

from .models import Asignacion
from services.models import Servicio
from drivers.models import Repartidor


class AsignarServicioForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        fields = ("servicio", "repartidor")
        widgets = {
            "servicio": forms.Select(attrs={"class": "ws-input form-select"}),
            "repartidor": forms.Select(attrs={"class": "ws-input form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["servicio"].queryset = Servicio.objects.select_related("empresa").order_by("-pk")
        self.fields["repartidor"].queryset = Repartidor.objects.select_related("usuario").order_by("nombres")


