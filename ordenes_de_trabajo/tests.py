from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from .models import OrdenTrabajo, EstadoOrden
from vehiculos.models import Vehiculo

User = get_user_model()


class OrdenTrabajoTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        
        self.user_mecanico = User.objects.create_user(
            username='mecanico1',
            password='contrasena123',
            rol='MECANICO'
        )
        self.user_consulta = User.objects.create_user(
            username='consulta1',
            password='contrasena123',
            rol='CONSULTA'
        )
        
        self.vehiculo = Vehiculo.objects.create(
            placa='ABC-123',
            modelo='Corolla',
            estado='EN_MANTENIMIENTO',
            kilometraje=50000
        )

    def test_crear_orden_sin_autenticacion(self):
        response = self.client.post('/api/ordenes-trabajo/', {
            'vehiculo': self.vehiculo.id,
            'descripcion_falla': 'Fallo de frenos'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_editar_orden_rol_consulta(self):
        orden = OrdenTrabajo.objects.create(
            vehiculo=self.vehiculo,
            descripcion_falla='Cambio de aceite'
        )
        self.client.force_authenticate(user=self.user_consulta)
        
        response = self.client.patch(f'/api/ordenes-trabajo/{orden.id}/', {
            'descripcion_falla': 'Intento de edición'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_impedir_ordenes_duplicadas_activas(self):
        self.client.force_authenticate(user=self.user_mecanico)
        
        # Primera orden activa
        OrdenTrabajo.objects.create(
            vehiculo=self.vehiculo,
            estado=EstadoOrden.ABIERTA,
            descripcion_falla='Falla inicial'
        )
        
        # Intento de crear segunda orden para el mismo vehículo
        response = self.client.post('/api/ordenes-trabajo/', {
            'vehiculo': self.vehiculo.id,
            'descripcion_falla': 'Segunda falla en paralelo'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bloqueo_edicion_orden_completada(self):
        self.client.force_authenticate(user=self.user_mecanico)
        orden = OrdenTrabajo.objects.create(
            vehiculo=self.vehiculo,
            estado=EstadoOrden.COMPLETADA,
            descripcion_falla='Servicio completado'
        )
        
        response = self.client.patch(f'/api/ordenes-trabajo/{orden.id}/', {
            'descripcion_falla': 'Intento de modificar texto'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validacion_estado_resuelta_requiere_fecha_salida(self):
        self.client.force_authenticate(user=self.user_mecanico)
        response = self.client.post('/api/ordenes-trabajo/', {
            'vehiculo': self.vehiculo.id,
            'estado': 'RESUELTA',
            'descripcion_falla': 'Reparación completada sin fecha de salida'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_salida', response.data)

    def test_validacion_fecha_salida_anterior_a_ingreso(self):
        self.client.force_authenticate(user=self.user_mecanico)
        response = self.client.post('/api/ordenes-trabajo/', {
            'vehiculo': self.vehiculo.id,
            'estado': 'RESUELTA',
            'fecha_ingreso': '2026-06-10T10:00:00Z',
            'fecha_salida': '2026-06-09T08:00:00Z',  # Es un día antes del ingreso
            'descripcion_falla': 'Prueba de coherencia en fechas'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_salida', response.data)

    def test_validacion_costo_total_negativo(self):
        self.client.force_authenticate(user=self.user_mecanico)
        response = self.client.post('/api/ordenes-trabajo/', {
            'vehiculo': self.vehiculo.id,
            'costo_total': -150.00,  # Valor negativo no permitido
            'descripcion_falla': 'Prueba de costo negativo'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('costo_total', response.data)