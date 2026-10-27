from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Proveedor
from inventario.models import Repuesto


class ProveedorTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin_proveedores',
            email='admin_proveedores@example.com',
            password='prueba12345'
        )

        self.client.force_authenticate(user=self.admin)

    def test_crear_proveedor(self):
        response = self.client.post('/api/proveedores/', {
            'cedula_juridica': '3101123456',
            'nombre': 'Repuestos Costa Rica',
            'contacto': '88888888'
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Proveedor.objects.count(), 1)

    def test_no_eliminar_proveedor_con_repuestos(self):
        proveedor = Proveedor.objects.create(
            cedula_juridica='3101123456',
            nombre='Repuestos CR',
            contacto='88888888'
        )

        Repuesto.objects.create(
            nombre='Filtro de aceite',
            codigo='FIL-01',
            stock=10,
            stock_minimo=2,
            precio_unitario=2500,
            proveedor=proveedor
        )

        response = self.client.delete(
            f'/api/proveedores/{proveedor.id}/'
        )

        self.assertEqual(response.status_code, 409)