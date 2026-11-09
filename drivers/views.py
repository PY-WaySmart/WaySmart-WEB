from django.views.generic import ListView

from .models import Repartidor


class RepartidorListView(ListView):
    model = Repartidor
    template_name = "drivers/list.html"
    context_object_name = "object_list"
