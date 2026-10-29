from django.urls import path

from . import views


urlpatterns = [
    path('auth/login/', views.VistaTokenLogin.as_view(), name='auth_login'),
    path('auth/logout/', views.logout_api, name='auth_logout'),
    path('auth/perfil/', views.perfil_api, name='auth_perfil'),
]
