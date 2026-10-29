from django.urls import path
from . import views

urlpatterns = [
    path('ordenes/', views.ordenes_api, name='ordenes_api'),
    path('ordenes/<int:id>/', views.orden_detalle_api, name='orden_detalle_api'),

    path('comentarios/', views.comentarios_api, name='comentarios_api'),
    path('comentarios/<int:pk>/', views.comentario_detalle_api, name='comentario_detalle_api'),
]
