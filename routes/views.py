from django.views.generic import ListView

from .models import Ruta


class RutaListView(ListView):
    model = Ruta
    template_name = "routes/list.html"
    context_object_name = "object_list"
