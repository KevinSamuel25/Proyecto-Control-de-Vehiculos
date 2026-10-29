from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Mantenimiento
from vehiculos.models import Vehiculo


class MantenimientoAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123',
        )
        self.client.force_authenticate(self.admin)

        self.vehiculo = Vehiculo.objects.create(
            placa='DEF-456',
            marca='Kia',
            modelo='Bongo',
            anio=2021,
            kilometraje=20000,
        )
        self.url = '/api/mantenimientos/'

    def test_no_permite_kilometraje_objetivo_menor_o_igual(self):
        respuesta = self.client.post(self.url, {
            'vehiculo': self.vehiculo.id,
            'descripcion': 'Cambio de aceite',
            'kilometraje_objetivo': 20000,
            'fecha_programada': '2026-11-01',
        })

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('kilometraje_objetivo', respuesta.data)

    def test_regla_de_negocio_se_protege_tambien_en_patch(self):
        mantenimiento = Mantenimiento.objects.create(
            vehiculo=self.vehiculo,
            descripcion='Revision general',
            kilometraje_objetivo=25000,
            fecha_programada='2026-11-01',
        )

        respuesta = self.client.patch(
            f'{self.url}{mantenimiento.id}/',
            {'kilometraje_objetivo': 15000},
            format='json',
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('kilometraje_objetivo', respuesta.data)

    def test_listado_filtra_por_vehiculo(self):
        mantenimiento = Mantenimiento.objects.create(
            vehiculo=self.vehiculo,
            descripcion='Revision general',
            kilometraje_objetivo=25000,
            fecha_programada='2026-11-01',
        )

        respuesta = self.client.get(self.url, {'vehiculo': self.vehiculo.id})

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['total_registros'], 1)
        self.assertEqual(respuesta.data['resultados'][0]['id'], mantenimiento.id)
