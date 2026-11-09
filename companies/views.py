from django.views.generic import ListView

from .models import Empresa


class EmpresaListView(ListView):
    model = Empresa
    template_name = "companies/list.html"
    context_object_name = "object_list"
