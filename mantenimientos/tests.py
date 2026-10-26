from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from vehiculos.models import Vehiculo
from .models import Mantenimiento


class MantenimientoAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123',
        )
        self.vehiculo = Vehiculo.objects.create(
            placa='DEF-456',
            marca='Kia',
            modelo='Bongo',
            anio=2021,
            kilometraje=20000,
        )
        self.url = '/api/mantenimientos/'

    def test_no_permite_kilometraje_objetivo_menor_o_igual(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, {
            'vehiculo': self.vehiculo.id,
            'descripcion': 'Cambio de aceite',
            'kilometraje_objetivo': 20000,
            'fecha_programada': '2026-11-01',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('kilometraje_objetivo', response.data)

    def test_listado_usa_relacion_del_vehiculo_y_filtra(self):
        mantenimiento = Mantenimiento.objects.create(
            vehiculo=self.vehiculo,
            descripcion='Revision general',
            kilometraje_objetivo=25000,
            fecha_programada='2026-11-01',
        )

        response = self.client.get(self.url, {'vehiculo': self.vehiculo.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_registros'], 1)
        self.assertEqual(response.data['resultados'][0]['id'], mantenimiento.id)
