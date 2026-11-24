from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from users.models import Perfil


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="empresa-demo",
            email="empresa@example.com",
            password="TestPass123!",
            is_active=True,
        )
        self.perfil = self.user.perfil
        self.perfil.rol = Perfil.Rol.EMPRESA
        self.perfil.estado = Perfil.Estado.ACTIVO
        self.perfil.save()

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={reverse('dashboard')}",
        )

    def test_empresa_can_open_dashboard(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")
        self.assertContains(response, "Centro de operaciones")


class RegistrationTests(TestCase):
    def test_registration_updates_signal_created_profile(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "first_name": "Ana",
                "last_name": "García",
                "username": "ana-garcia",
                "email": "ana@example.com",
                "role": Perfil.Rol.EMPRESA,
                "password": "Qx7!vV3z#9pLm2",
                "password_confirmation": "Qx7!vV3z#9pLm2",
                "terms": "on",
            },
        )

        self.assertRedirects(response, reverse("users:login"))
        user = get_user_model().objects.get(username="ana-garcia")
        self.assertEqual(Perfil.objects.filter(usuario=user).count(), 1)
        self.assertEqual(user.perfil.rol, Perfil.Rol.EMPRESA)
        self.assertEqual(user.perfil.estado, Perfil.Estado.PENDIENTE)
