from django.urls import path

from . import views


urlpatterns = [
    path('vehiculos/', views.vehiculos_api, name='vehiculos_api'),
    path('vehiculos/<int:pk>/', views.vehiculo_detalle_api, name='vehiculo_detalle_api'),
]

