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
