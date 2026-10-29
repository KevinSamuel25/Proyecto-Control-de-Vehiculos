from django.contrib.auth.models import Group, User
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
        grupo_operador, _ = Group.objects.get_or_create(name='Operador')
        self.operador = User.objects.create_user(
            username='operador',
            password='password123',
        )
        self.operador.groups.add(grupo_operador)

        self.url = '/api/vehiculos/'
        self.vehiculo = Vehiculo.objects.create(
            placa='ABC-123',
            marca='Toyota',
            modelo='Hilux',
            anio=2022,
            kilometraje=10000,
        )

    def test_listado_paginado_y_filtrado_por_estado(self):
        self.client.force_authenticate(self.operador)
        respuesta = self.client.get(self.url, {'estado': 'ACTIVO'})

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['total_registros'], 1)
        self.assertEqual(respuesta.data['resultados'][0]['placa'], 'ABC-123')
        self.assertIn('total_paginas', respuesta.data)

    def test_anonimo_recibe_401(self):
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crear_vehiculo_requiere_administrador(self):
        datos = {
            'placa': 'xyz-789',
            'marca': 'Nissan',
            'modelo': 'Frontier',
            'anio': 2023,
            'kilometraje': 0,
        }

        self.client.force_authenticate(self.operador)
        respuesta = self.client.post(self.url, datos)
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.admin)
        respuesta = self.client.post(self.url, datos)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data['placa'], 'XYZ-789')

    def test_placa_invalida_es_rechazada(self):
        self.client.force_authenticate(self.admin)
        respuesta = self.client.post(self.url, {
            'placa': 'placa invalida',
            'marca': 'Ford',
            'modelo': 'Ranger',
            'anio': 2023,
            'kilometraje': 100,
        })

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('placa', respuesta.data)

    def test_placa_duplicada_es_rechazada(self):
        self.client.force_authenticate(self.admin)
        respuesta = self.client.post(self.url, {
            'placa': 'ABC-123',
            'marca': 'Toyota',
            'modelo': 'Hilux',
            'anio': 2022,
            'kilometraje': 0,
        })

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('placa', respuesta.data)
