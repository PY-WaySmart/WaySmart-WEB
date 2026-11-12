from django.views.generic import ListView

from .models import Servicio


class ServicioListView(ListView):
    model = Servicio
    template_name = "services/list.html"
    context_object_name = "object_list"
