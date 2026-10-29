from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APITestCase

from vehiculos.models import Vehiculo
from .models import OrdenTrabajo


class OrdenTrabajoTests(APITestCase):

    def setUp(self):
        grupo_operador, _ = Group.objects.get_or_create(name='Operador')
        grupo_consulta, _ = Group.objects.get_or_create(name='Consulta')

        self.admin = User.objects.create_superuser(
            username='admin',
            password='password123',
        )
        self.operador = User.objects.create_user(
            username='operador1',
            password='contrasena123',
        )
        self.operador.groups.add(grupo_operador)
        self.consulta = User.objects.create_user(
            username='consulta1',
            password='contrasena123',
        )
        self.consulta.groups.add(grupo_consulta)

        self.vehiculo = Vehiculo.objects.create(
            placa='GHI-789',
            marca='Toyota',
            modelo='Corolla',
            anio=2020,
            kilometraje=50000,
        )

    def crear_orden(self, **kwargs):
        datos = {
            'vehiculo': self.vehiculo.id,
            'descripcion_falla': 'Fallo de frenos',
        }
        datos.update(kwargs)
        return datos

    def test_crear_orden_sin_autenticacion_devuelve_401(self):
        respuesta = self.client.post('/api/ordenes/', self.crear_orden())
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rol_consulta_no_puede_crear_orden(self):
        self.client.force_authenticate(user=self.consulta)
        respuesta = self.client.post('/api/ordenes/', self.crear_orden())
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_eliminar_orden_requiere_administrador(self):
        orden = OrdenTrabajo.objects.create(
            vehiculo=self.vehiculo,
            descripcion_falla='Cambio de aceite',
        )

        self.client.force_authenticate(user=self.operador)
        respuesta = self.client.delete(f'/api/ordenes/{orden.id}/')
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        respuesta = self.client.delete(f'/api/ordenes/{orden.id}/')
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)

    def test_operador_puede_crear_orden_y_se_genera_codigo(self):
        self.client.force_authenticate(user=self.operador)
        respuesta = self.client.post('/api/ordenes/', self.crear_orden())

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(respuesta.data['codigo'].startswith('OT-'))

    def test_consultar_orden_inexistente_devuelve_404(self):
        self.client.force_authenticate(user=self.consulta)
        respuesta = self.client.get('/api/ordenes/9999/')
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    def test_impedir_ordenes_duplicadas_activas(self):
        self.client.force_authenticate(user=self.operador)
        OrdenTrabajo.objects.create(
            vehiculo=self.vehiculo,
            estado='ABIERTA',
            descripcion_falla='Falla inicial',
        )

        respuesta = self.client.post('/api/ordenes/', self.crear_orden())
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bloqueo_edicion_orden_completada_en_patch(self):
        orden = OrdenTrabajo.objects.create(
            vehiculo=self.vehiculo,
            estado='COMPLETADA',
            fecha_salida='2026-10-20T10:00:00Z',
            descripcion_falla='Servicio completado',
        )

        self.client.force_authenticate(user=self.operador)
        respuesta = self.client.patch(
            f'/api/ordenes/{orden.id}/',
            {'descripcion_falla': 'Intento de modificar texto'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_completar_orden_requiere_fecha_salida(self):
        orden = OrdenTrabajo.objects.create(
            vehiculo=self.vehiculo,
            descripcion_falla='Reparación de motor',
        )

        self.client.force_authenticate(user=self.operador)
        respuesta = self.client.patch(
            f'/api/ordenes/{orden.id}/',
            {'estado': 'COMPLETADA'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_salida', respuesta.data)

    def test_fecha_salida_anterior_a_ingreso_es_rechazada(self):
        orden = OrdenTrabajo.objects.create(
            vehiculo=self.vehiculo,
            descripcion_falla='Prueba de coherencia en fechas',
        )

        self.client.force_authenticate(user=self.operador)
        respuesta = self.client.patch(
            f'/api/ordenes/{orden.id}/',
            {'fecha_salida': '2020-01-01T08:00:00Z'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_salida', respuesta.data)

    def test_costo_total_negativo_es_rechazado(self):
        self.client.force_authenticate(user=self.operador)
        respuesta = self.client.post(
            '/api/ordenes/',
            self.crear_orden(costo_total='-150.00'),
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('costo_total', respuesta.data)
