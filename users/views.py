from django.views.generic import ListView

from .models import Perfil


class PerfilListView(ListView):
    model = Perfil
    template_name = "users/list.html"
    context_object_name = "object_list"
