from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from companies.models import Empresa
from drivers.models import Repartidor
from routes.models import Asignacion
from services.models import Destino, Servicio
from users.admin import _sync_user_access
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

    def test_company_pages_render_with_role_scoped_lists(self):
        self.client.force_login(self.user)

        for route_name in (
            "companies:list",
            "services:list",
            "routes:list",
            "drivers:list",
            "payments:list",
        ):
            with self.subTest(route=route_name):
                self.assertEqual(self.client.get(reverse(route_name)).status_code, 200)


class RegistrationTests(TestCase):
    def test_registration_form_renders(self):
        response = self.client.get(reverse("users:register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Datos de la empresa")
        self.assertContains(response, "Datos del repartidor")

    def test_registration_updates_signal_created_profile(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "first_name": "Ana",
                "last_name": "García",
                "username": "ana-garcia",
                "email": "ana@example.com",
                "role": Perfil.Rol.EMPRESA,
                "business_name": "WaySmart Envíos",
                "nit": "900123456",
                "business_address": "Calle 1 # 2-3",
                "business_phone": "3001234567",
                "legal_name": "Ana García",
                "legal_phone": "3001234567",
                "legal_email": "ana@example.com",
                "tipo_colaboracion": Empresa.TipoColaboracion.SOCIO,
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
        empresa = Empresa.objects.get(usuario=user)
        self.assertEqual(empresa.nit, "900123456")
        self.assertEqual(empresa.estado, Empresa.Estado.PENDIENTE)

        user.perfil.estado = Perfil.Estado.ACTIVO
        user.perfil.save()
        _sync_user_access(user.perfil)
        empresa.refresh_from_db()
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(empresa.estado, Empresa.Estado.APROBADO)
        self.assertIsNotNone(empresa.fecha_validacion)

    def test_driver_registration_creates_driver_profile(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "first_name": "Luis",
                "last_name": "Pérez",
                "username": "luis-repartidor",
                "email": "luis@example.com",
                "role": Perfil.Rol.REPARTIDOR,
                "identification": "123456789",
                "phone": "3007654321",
                "password": "Qx7!vV3z#9pLm2",
                "password_confirmation": "Qx7!vV3z#9pLm2",
                "terms": "on",
            },
        )

        self.assertRedirects(response, reverse("users:login"))
        user = get_user_model().objects.get(username="luis-repartidor")
        self.assertEqual(user.perfil.rol, Perfil.Rol.REPARTIDOR)
        repartidor = Repartidor.objects.get(usuario=user)
        self.assertEqual(repartidor.nro_identificacion, "123456789")
        self.assertEqual(repartidor.estado, "Pendiente")

        user.perfil.estado = Perfil.Estado.ACTIVO
        user.perfil.save()
        _sync_user_access(user.perfil)
        repartidor.refresh_from_db()
        self.assertEqual(repartidor.estado, "Activo")
        self.assertIsNotNone(repartidor.fecha_validacion)


class ServiceRequestTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="empresa-servicios",
            email="servicios@example.com",
            password="TestPass123!",
            is_active=True,
        )
        self.user.perfil.rol = Perfil.Rol.EMPRESA
        self.user.perfil.estado = Perfil.Estado.ACTIVO
        self.user.perfil.save()
        self.empresa = Empresa.objects.create(
            usuario=self.user,
            nombre="Empresa de prueba",
            nit="900987654",
            direccion="Calle 1",
            telefono_contacto="3000000000",
            representante_legal_nombre="Ana",
            representante_legal_telefono="3000000000",
            representante_legal_correo="ana@empresa.com",
            tipo_colaboracion=Empresa.TipoColaboracion.SOCIO,
            estado=Empresa.Estado.APROBADO,
        )
        self.client.force_login(self.user)

    def test_company_can_request_service_and_first_destination(self):
        response = self.client.post(
            reverse("services:create"),
            {
                "codigo_servicio": "WS-100",
                "tipo_envio": "Paquete",
                "cantidad_entregas": 1,
                "direccion_recogidas": "Bodega central",
                "observaciones": "",
                "destinos-TOTAL_FORMS": "2",
                "destinos-INITIAL_FORMS": "0",
                "destinos-0-nombre_destinatario": "Carlos",
                "destinos-0-telefono_destinatario": "3001112233",
                "destinos-0-direccion_destino": "Carrera 2 # 3-4",
                "destinos-0-prioridad": Destino.Prioridad.ALTA,
                "destinos-1-nombre_destinatario": "María",
                "destinos-1-telefono_destinatario": "3004445566",
                "destinos-1-direccion_destino": "Calle 5 # 6-7",
                "destinos-1-prioridad": Destino.Prioridad.MEDIA,
            },
        )

        self.assertRedirects(response, reverse("services:list"))
        servicio = Servicio.objects.get(codigo_servicio="WS-100")
        self.assertEqual(servicio.empresa, self.empresa)
        self.assertEqual(servicio.cantidad_entregas, 2)
        self.assertEqual(servicio.destinos.count(), 2)

    def test_company_must_be_approved_before_requesting_service(self):
        self.empresa.estado = Empresa.Estado.PENDIENTE
        self.empresa.save(update_fields=["estado"])

        response = self.client.post(
            reverse("services:create"),
            {"codigo_servicio": "WS-PENDING"},
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertFalse(Servicio.objects.filter(codigo_servicio="WS-PENDING").exists())

    def test_service_request_requires_at_least_one_destination(self):
        response = self.client.post(
            reverse("services:create"),
            {
                "codigo_servicio": "WS-NO-DEST",
                "direccion_recogidas": "Bodega central",
                "destinos-TOTAL_FORMS": "1",
                "destinos-INITIAL_FORMS": "0",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["destinos"].non_form_errors())
        self.assertFalse(Servicio.objects.filter(codigo_servicio="WS-NO-DEST").exists())


class RoleProfileEditTests(TestCase):
    def test_company_can_update_its_own_profile(self):
        user = get_user_model().objects.create_user(
            username="empresa-perfil",
            email="perfil-empresa@example.com",
            password="TestPass123!",
            is_active=True,
        )
        user.perfil.rol = Perfil.Rol.EMPRESA
        user.perfil.estado = Perfil.Estado.ACTIVO
        user.perfil.save()
        Empresa.objects.create(
            usuario=user,
            nombre="Empresa original",
            nit="900111222",
            direccion="Calle 1",
            telefono_contacto="3000000000",
            representante_legal_nombre="Ana",
            representante_legal_telefono="3000000000",
            representante_legal_correo="ana@empresa.com",
            tipo_colaboracion=Empresa.TipoColaboracion.SOCIO,
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("companies:profile"),
            {
                "nombre": "Empresa actualizada",
                "nit": "900111222",
                "direccion": "Calle 2",
                "telefono_contacto": "3000000001",
                "representante_legal_nombre": "Ana",
                "representante_legal_telefono": "3000000000",
                "representante_legal_correo": "ana@empresa.com",
                "tipo_colaboracion": Empresa.TipoColaboracion.SOCIO,
            },
        )

        self.assertRedirects(response, reverse("companies:list"))
        self.assertEqual(Empresa.objects.get(usuario=user).nombre, "Empresa actualizada")

    def test_driver_can_update_its_own_profile(self):
        user = get_user_model().objects.create_user(
            username="repartidor-perfil",
            email="perfil-repartidor@example.com",
            password="TestPass123!",
            is_active=True,
        )
        user.perfil.rol = Perfil.Rol.REPARTIDOR
        user.perfil.estado = Perfil.Estado.ACTIVO
        user.perfil.save()
        Repartidor.objects.create(
            usuario=user,
            nombres="Luis",
            apellidos="Pérez",
            nro_identificacion="123456789",
            telefono="3000000000",
            estado="Activo",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("drivers:profile"),
            {
                "nombres": "Luis Alberto",
                "apellidos": "Pérez",
                "nro_identificacion": "123456789",
                "telefono": "3000000001",
            },
        )

        self.assertRedirects(response, reverse("drivers:list"))
        self.assertEqual(Repartidor.objects.get(usuario=user).nombres, "Luis Alberto")


class AssignmentWorkflowTests(TestCase):
    def test_staff_can_open_assignment_form(self):
        staff_user = get_user_model().objects.create_user(
            username="staff-ops",
            email="staff@example.com",
            password="TestPass123!",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse("routes:assign"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "routes/assign.html")

    def test_driver_can_accept_then_complete_own_assignment(self):
        user = get_user_model().objects.create_user(
            username="repartidor-demo",
            email="repartidor@example.com",
            password="TestPass123!",
            is_active=True,
        )
        user.perfil.rol = Perfil.Rol.REPARTIDOR
        user.perfil.estado = Perfil.Estado.ACTIVO
        user.perfil.save()
        driver = Repartidor.objects.create(usuario=user, nombres="Luis", estado="Activo")
        company_user = get_user_model().objects.create_user(
            username="empresa-demo-2",
            email="empresa2@example.com",
            password="TestPass123!",
        )
        empresa = Empresa.objects.create(
            usuario=company_user,
            nombre="Empresa de prueba",
            nit="900222333",
            direccion="Calle 1",
            telefono_contacto="3000000000",
            representante_legal_nombre="Ana",
            representante_legal_telefono="3000000000",
            representante_legal_correo="ana@empresa.com",
            tipo_colaboracion=Empresa.TipoColaboracion.SOCIO,
        )
        service = Servicio.objects.create(
            empresa=empresa,
            codigo_servicio="WS-200",
            direccion_recogidas="Bodega central",
        )
        assignment = Asignacion.objects.create(
            servicio=service,
            repartidor=driver,
            estado="Pendiente",
        )
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("drivers:list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("payments:list")).status_code, 200)

        accepted = self.client.post(
            reverse("routes:update_assignment", args=[assignment.pk]),
            {"estado": "Aceptada"},
        )
        assignment.refresh_from_db()
        self.assertRedirects(accepted, reverse("routes:list"))
        self.assertEqual(assignment.estado, "Aceptada")
        self.assertIsNotNone(assignment.fecha_aceptacion)
        service.refresh_from_db()
        self.assertEqual(service.estado, Servicio.Estado.EN_PROCESO)

        completed = self.client.post(
            reverse("routes:update_assignment", args=[assignment.pk]),
            {"estado": "Completada"},
        )
        assignment.refresh_from_db()
        self.assertRedirects(completed, reverse("routes:list"))
        self.assertEqual(assignment.estado, "Completada")
        service.refresh_from_db()
        self.assertEqual(service.estado, Servicio.Estado.COMPLETADO)

    def test_driver_cannot_update_another_drivers_assignment(self):
        user = get_user_model().objects.create_user(
            username="repartidor-ajeno",
            email="ajeno@example.com",
            password="TestPass123!",
            is_active=True,
        )
        user.perfil.rol = Perfil.Rol.REPARTIDOR
        user.perfil.estado = Perfil.Estado.ACTIVO
        user.perfil.save()
        owner = get_user_model().objects.create_user(
            username="repartidor-propietario",
            email="propietario@example.com",
            password="TestPass123!",
            is_active=True,
        )
        Repartidor.objects.create(usuario=owner, nombres="Propietario")
        company_user = get_user_model().objects.create_user(
            username="empresa-asignacion",
            email="empresa-asignacion@example.com",
            password="TestPass123!",
        )
        empresa = Empresa.objects.create(
            usuario=company_user,
            nombre="Empresa asignación",
            nit="900888111",
            direccion="Calle 1",
            telefono_contacto="3000000000",
            representante_legal_nombre="Ana",
            representante_legal_telefono="3000000000",
            representante_legal_correo="ana@empresa.com",
            tipo_colaboracion=Empresa.TipoColaboracion.SOCIO,
        )
        service = Servicio.objects.create(
            empresa=empresa,
            codigo_servicio="WS-403",
            direccion_recogidas="Bodega central",
        )
        assignment = Asignacion.objects.create(
            servicio=service,
            repartidor=owner.repartidor,
            estado="Pendiente",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("routes:update_assignment", args=[assignment.pk]),
            {"estado": "Aceptada"},
        )
        self.assertEqual(response.status_code, 403)


class UserAdminDeleteTests(TestCase):
    def test_admin_can_delete_user_after_confirmation(self):
        user_model = get_user_model()
        admin_user = user_model.objects.create_superuser(
            username="admin-delete",
            email="admin-delete@example.com",
            password="TestPass123!",
        )
        user = user_model.objects.create_user(
            username="delete-me",
            email="delete-me@example.com",
            password="TestPass123!",
        )
        self.client.force_login(admin_user)

        changelist_url = reverse(
            f"admin:{user_model._meta.app_label}_{user_model._meta.model_name}_changelist"
        )
        response = self.client.get(changelist_url)
        self.assertContains(response, "Eliminar")

        action_url = reverse(
            f"admin:{user_model._meta.app_label}_{user_model._meta.model_name}_delete_user",
            args=[user.pk],
        )
        delete_url = reverse(
            f"admin:{user_model._meta.app_label}_{user_model._meta.model_name}_delete",
            args=[user.pk],
        )
        response = self.client.get(action_url)
        self.assertRedirects(response, delete_url, fetch_redirect_response=False)

        confirmation = self.client.get(delete_url)
        self.assertEqual(confirmation.status_code, 200)

        response = self.client.post(delete_url, {"post": "yes"})
        self.assertRedirects(response, changelist_url)
        self.assertFalse(user_model.objects.filter(pk=user.pk).exists())

    def test_admin_cannot_delete_user_with_protected_company(self):
        user_model = get_user_model()
        admin_user = user_model.objects.create_superuser(
            username="admin-protected-delete",
            email="admin-protected-delete@example.com",
            password="TestPass123!",
        )
        user = user_model.objects.create_user(
            username="company-user",
            email="company-user@example.com",
            password="TestPass123!",
        )
        Empresa.objects.create(
            usuario=user,
            nombre="Empresa protegida",
            nit="900333444",
            direccion="Calle 1",
            telefono_contacto="3000000000",
            representante_legal_nombre="Ana",
            representante_legal_telefono="3000000000",
            representante_legal_correo="ana@empresa.com",
            tipo_colaboracion=Empresa.TipoColaboracion.SOCIO,
        )
        self.client.force_login(admin_user)

        delete_url = reverse(
            f"admin:{user_model._meta.app_label}_{user_model._meta.model_name}_delete",
            args=[user.pk],
        )
        confirmation = self.client.get(delete_url)
        self.assertContains(confirmation, "Empresa protegida")

        response = self.client.post(delete_url, {"post": "yes"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user_model.objects.filter(pk=user.pk).exists())
