from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Vehiculo


class VehiculoAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123',
        )
        self.url = '/api/vehiculos/'
        self.vehiculo = Vehiculo.objects.create(
            placa='ABC-123',
            marca='Toyota',
            modelo='Hilux',
            anio=2022,
            kilometraje=10000,
        )

    def test_listado_paginado_y_filtrado_por_estado(self):
        response = self.client.get(self.url, {'estado': 'ACTIVO'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_registros'], 1)
        self.assertEqual(response.data['resultados'][0]['placa'], 'ABC-123')

    def test_crear_vehiculo_requiere_administrador(self):
        data = {
            'placa': 'xyz-789',
            'marca': 'Nissan',
            'modelo': 'Frontier',
            'anio': 2023,
            'kilometraje': 0,
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['placa'], 'XYZ-789')

    def test_placa_invalida_es_rechazada(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.url, {
            'placa': 'placa invalida',
            'marca': 'Ford',
            'modelo': 'Ranger',
            'anio': 2023,
            'kilometraje': 100,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('placa', response.data)
