from django.views.generic import ListView

from .models import PagoRepartidor


class PagoRepartidorListView(ListView):
    model = PagoRepartidor
    template_name = "payments/list.html"
    context_object_name = "object_list"
