from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APITestCase


class AutenticacionTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            password='password123',
        )
        grupo, _ = Group.objects.get_or_create(name='Operador')
        self.operador = User.objects.create_user(
            username='operador',
            password='password123',
        )
        self.operador.groups.add(grupo)

    def test_login_devuelve_token_y_roles(self):
        respuesta = self.client.post('/api/auth/login/', {
            'username': 'operador',
            'password': 'password123',
        })

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn('token', respuesta.data)
        self.assertIn('Operador', respuesta.data['usuario']['roles'])

    def test_login_con_credenciales_invalidas_devuelve_400(self):
        respuesta = self.client.post('/api/auth/login/', {
            'username': 'operador',
            'password': 'incorrecta',
        })

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_perfil_sin_token_devuelve_401(self):
        respuesta = self.client.get('/api/auth/perfil/')
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_perfil_con_token_devuelve_usuario_y_roles(self):
        self.client.force_authenticate(user=self.admin)
        respuesta = self.client.get('/api/auth/perfil/')

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['username'], 'admin')
        self.assertIn('Administrador', respuesta.data['roles'])

    def test_logout_invalida_el_token(self):
        login = self.client.post('/api/auth/login/', {
            'username': 'operador',
            'password': 'password123',
        })
        token = login.data['token']

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        respuesta = self.client.post('/api/auth/logout/')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        respuesta = self.client.get('/api/auth/perfil/')
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)
