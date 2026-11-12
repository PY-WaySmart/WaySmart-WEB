from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import ListView
from .models import Perfil


class PerfilListView(ListView):
    model = Perfil
    template_name = 'users/list.html'
    context_object_name = 'object_list'


def login_view(request):
    # Si ya inició sesión, lo mandamos directo a su panel
    if request.user.is_authenticated:
        return redirigir_por_rol(request.user)

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        # Buscamos el usuario por correo electrónico
        user_obj = User.objects.filter(email=email).first()

        if user_obj is not None:
            user = authenticate(request, username=user_obj.username, password=password)
        else:
            user = None

        if user is not None:
            # Verificamos que la cuenta de Django esté activa
            if not user.is_active:
                messages.error(request, 'Tu cuenta está desactivada. Contacta al administrador.')
                return render(request, 'users/login.html')

            # Verificamos el perfil y su estado en WaySmart
            perfil = getattr(user, 'perfil', None)
            if perfil is None:
                messages.error(request, 'Tu usuario no tiene un perfil asignado.')
                return render(request, 'users/login.html')

            if perfil.estado != Perfil.Estado.ACTIVO:
                messages.error(request, 'Tu cuenta está inactiva o bloqueada.')
                return render(request, 'users/login.html')

            # Todo en orden: iniciamos sesión y redirigimos
            login(request, user)
            return redirigir_por_rol(user)
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'users/login.html')


def redirigir_por_rol(user):
    perfil = getattr(user, 'perfil', None)

    if user.is_superuser or (perfil and perfil.rol == Perfil.Rol.ADMINISTRADOR):
        return redirect('/admin/')
    elif perfil and perfil.rol == Perfil.Rol.EMPRESA:
        return redirect('/empresas/')
    elif perfil and perfil.rol == Perfil.Rol.REPARTIDOR:
        return redirect('/repartidores/')

    return redirect('home')