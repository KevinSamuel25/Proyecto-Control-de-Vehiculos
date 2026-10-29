from django.contrib.auth.models import Group, User
from rest_framework.test import APITestCase

from proveedores.models import Proveedor
from vehiculos.models import Vehiculo
from ordenes_de_trabajo.models import OrdenTrabajo, ComentarioOrden

from .models import Repuesto


class InventarioTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin_inventario',
            email='admin_inventario@example.com',
            password='prueba12345'
        )

        self.client.force_authenticate(user=self.admin)

        self.proveedor = Proveedor.objects.create(
            cedula_juridica='3101987654',
            nombre='Distribuidora',
            contacto='88887777'
        )

        self.repuesto = Repuesto.objects.create(
            nombre='Filtro de aceite',
            codigo='FIL-01',
            stock=5,
            stock_minimo=2,
            precio_unitario=2500,
            proveedor=self.proveedor
        )

    def crear_orden(self):
        vehiculo = Vehiculo.objects.create(
            placa='ABC-123',
            marca='Toyota',
            modelo='Hilux',
            anio=2022,
            kilometraje=10000
        )

        return OrdenTrabajo.objects.create(
            codigo='OT-P3-001',
            vehiculo=vehiculo,
            descripcion_falla='Cambio de aceite'
        )

    def test_crear_repuesto(self):
        respuesta = self.client.post('/api/inventario/', {
            'nombre': 'Pastillas de freno',
            'codigo': 'FRE-02',
            'stock': 15,
            'stock_minimo': 3,
            'precio_unitario': '9500.00',
            'proveedor': self.proveedor.id
        })

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Repuesto.objects.count(), 2)

    def test_filtrar_stock_bajo(self):
        respuesta = self.client.get(
            '/api/inventario/',
            {'bajo_stock': '1'}
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['total_registros'], 0)

    def test_no_permitir_stock_negativo(self):
        respuesta = self.client.patch(
            f'/api/inventario/{self.repuesto.id}/',
            {'stock': -5},
            format='json'
        )

        self.assertEqual(respuesta.status_code, 400)

    def test_descontar_stock(self):
        orden = self.crear_orden()

        respuesta = self.client.post(
            '/api/inventario/consumos/',
            {
                'orden': orden.id,
                'repuesto': self.repuesto.id,
                'cantidad': 2
            },
            format='json'
        )

        self.assertEqual(respuesta.status_code, 201)

        self.repuesto.refresh_from_db()
        orden.refresh_from_db()

        self.assertEqual(self.repuesto.stock, 3)
        self.assertEqual(orden.costo_total, 5000)
        self.assertEqual(ComentarioOrden.objects.count(), 1)

    def test_stock_insuficiente(self):
        orden = self.crear_orden()

        respuesta = self.client.post(
            '/api/inventario/consumos/',
            {
                'orden': orden.id,
                'repuesto': self.repuesto.id,
                'cantidad': 10
            },
            format='json'
        )

        self.assertEqual(respuesta.status_code, 400)

        self.repuesto.refresh_from_db()

        self.assertEqual(self.repuesto.stock, 5)
        self.assertEqual(ComentarioOrden.objects.count(), 0)

    def test_no_eliminar_repuesto_utilizado(self):
        orden = self.crear_orden()

        self.client.post(
            '/api/inventario/consumos/',
            {
                'orden': orden.id,
                'repuesto': self.repuesto.id,
                'cantidad': 1
            },
            format='json'
        )

        respuesta = self.client.delete(
            f'/api/inventario/{self.repuesto.id}/'
        )

        self.assertEqual(respuesta.status_code, 409)


class InventarioPermisosTests(APITestCase):

    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            cedula_juridica='3101987654',
            nombre='Distribuidora',
            contacto='88887777'
        )

    def test_anonimo_no_accede_al_inventario(self):
        respuesta = self.client.get('/api/inventario/')
        self.assertEqual(respuesta.status_code, 401)

    def test_rol_consulta_no_puede_crear_repuesto(self):
        grupo, _ = Group.objects.get_or_create(name='Consulta')
        consulta = User.objects.create_user(
            username='consulta_inv',
            password='prueba12345',
        )
        consulta.groups.add(grupo)
        self.client.force_authenticate(user=consulta)

        respuesta = self.client.post('/api/inventario/', {
            'nombre': 'Bateria',
            'codigo': 'BAT-01',
            'stock': 4,
            'stock_minimo': 1,
            'precio_unitario': '45000.00',
            'proveedor': self.proveedor.id,
        })

        self.assertEqual(respuesta.status_code, 403)
