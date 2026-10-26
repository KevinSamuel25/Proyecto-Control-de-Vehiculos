from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import EquipoArena, OrdenTrabajo, ComentarioOrden

class ArenaAPITests(APITestCase):

    def setUp(self):

        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@arena.com', password='password123'
        )
        self.regular_user = User.objects.create_user(
            username='user', email='user@arena.com', password='password123'
        )


        self.orden = OrdenTrabajo.objects.create(
            titulo='Fallo de tarjeta gráfica',
            descripcion='La PC se apaga al abrir juegos pesados.',
            estado='PENDIENTE',
            prioridad='ALTA',
            costo_estimado=150.00
        )

        self.url_ordenes = '/api/ordenes/'
        self.url_comentarios = '/api/comentarios/'

    # =========================================================================
    # TESTS PARA EQUIPOS DE ARENA
    # =========================================================================

    def test_listar_equipos_con_filtros_y_paginacion(self):
        """Prueba que el listado responda paginado y filtre correctamente por tipo y estado activo."""
        response = self.client.get(self.url_equipos, {'tipo': 'PC', 'activo': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Validar estructura de respuesta paginada
        self.assertIn('resultados', response.data)
        self.assertIn('total_registros', response.data)
        self.assertEqual(response.data['total_registros'], 1)
        self.assertEqual(response.data['resultados'][0]['codigo'], 'PC-01')

    def test_crear_equipo_como_admin(self):
        """Un administrador debe poder crear un equipo exitosamente."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'codigo': 'VR-01',
            'nombre': 'Oculus Quest 3',
            'tipo': 'Realidad Virtual',
            'ubicacion': 'Zona VR',
            'activo': True
        }
        response = self.client.post(self.url_equipos, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EquipoArena.objects.count(), 3)

    def test_crear_equipo_como_usuario_regular_prohibido(self):
        """Un usuario normal no debe poder crear un equipo (requiere staff)."""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'codigo': 'VR-02',
            'nombre': 'HTC Vive',
            'tipo': 'Realidad Virtual',
            'ubicacion': 'Zona VR',
            'activo': True
        }
        response = self.client.post(self.url_equipos, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =========================================================================
    # TESTS PARA ÓRDENES DE TRABAJO Y VALIDACIONES
    # =========================================================================

    def test_crear_orden_trabajo_costo_negativo_falla(self):
        """El serializer debe rechazar costos negativos por regla de validación."""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'titulo': 'Mantenimiento preventivo',
            'descripcion': 'Limpieza general',
            'estado': 'PENDIENTE',
            'prioridad': 'MEDIA',
            'equipo': self.equipo1.id,
            'costo_estimado': -50.00  # Costo inválido
        }
        response = self.client.post(self.url_ordenes, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('costo_estimado', response.data)

    def test_crear_orden_resuelta_sin_fecha_resolucion_falla(self):
        """Si el estado es RESUELTA, la validación exige fecha de resolución."""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'titulo': 'Reparación de puerto USB',
            'descripcion': 'Cambio de placa frontal',
            'estado': 'RESUELTA',  
            'prioridad': 'BAJA',
            'equipo': self.equipo1.id,
            'costo_estimado': 30.00,
            'fecha_resolucion': None 
        }
        response = self.client.post(self.url_ordenes, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_resolucion', response.data)

    # =========================================================================
    # TESTS PARA COMENTARIOS DE ÓRDENES
    # =========================================================================

    def test_crear_comentario_asigna_autor_automaticamente(self):
        """El comentario debe registrar automáticamente al usuario autenticado como autor."""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'orden': self.orden.id,
            'texto': 'Revisé los voltajes y la fuente está fallando.'
        }
        response = self.client.post(self.url_comentarios, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el autor asignado coincida con el usuario autenticado
        comentario_creado = ComentarioOrden.objects.get(id=response.data['id'])
        self.assertEqual(comentario_creado.autor, self.regular_user)
        self.assertEqual(comentario_creado.autor_username, 'user')