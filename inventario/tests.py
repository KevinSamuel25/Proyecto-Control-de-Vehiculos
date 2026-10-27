from django.contrib.auth.models import User
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
        response = self.client.post('/api/inventario/', {
            'nombre': 'Pastillas de freno',
            'codigo': 'FRE-02',
            'stock': 15,
            'stock_minimo': 3,
            'precio_unitario': '9500.00',
            'proveedor': self.proveedor.id
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Repuesto.objects.count(), 2)

    def test_filtrar_stock_bajo(self):
        response = self.client.get(
            '/api/inventario/',
            {'bajo_stock': '1'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_registros'], 0)

    def test_no_permitir_stock_negativo(self):
        response = self.client.patch(
            f'/api/inventario/{self.repuesto.id}/',
            {'stock': -5},
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_descontar_stock(self):
        orden = self.crear_orden()

        response = self.client.post(
            '/api/inventario/consumos/',
            {
                'orden': orden.id,
                'repuesto': self.repuesto.id,
                'cantidad': 2
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        self.repuesto.refresh_from_db()
        orden.refresh_from_db()

        self.assertEqual(self.repuesto.stock, 3)
        self.assertEqual(orden.costo_total, 5000)
        self.assertEqual(ComentarioOrden.objects.count(), 1)

    def test_stock_insuficiente(self):
        orden = self.crear_orden()

        response = self.client.post(
            '/api/inventario/consumos/',
            {
                'orden': orden.id,
                'repuesto': self.repuesto.id,
                'cantidad': 10
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

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

        response = self.client.delete(
            f'/api/inventario/{self.repuesto.id}/'
        )

        self.assertEqual(response.status_code, 409)