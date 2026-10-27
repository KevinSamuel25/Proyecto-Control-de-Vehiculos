from django.urls import path
from . import views

urlpatterns = [
    path('inventario/', views.inventario_api, name='inventario_api'),
    path('inventario/resumen/', views.resumen_inventario_api, name='resumen_inventario_api'),
    path('inventario/consumos/', views.consumo_repuesto_api, name='consumo_repuesto_api'),
    path('inventario/<int:pk>/', views.repuesto_detalle_api, name='repuesto_detalle_api'),
]