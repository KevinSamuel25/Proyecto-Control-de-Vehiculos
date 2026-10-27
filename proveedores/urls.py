from django.urls import path
from . import views

urlpatterns = [
    path('proveedores/', views.proveedores_api, name='proveedores_api'),
    path('proveedores/<int:pk>/', views.proveedor_detalle_api, name='proveedor_detalle_api'),
]