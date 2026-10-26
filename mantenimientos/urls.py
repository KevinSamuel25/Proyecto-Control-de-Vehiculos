from django.urls import path

from . import views


urlpatterns = [
    path('mantenimientos/', views.mantenimientos_api, name='mantenimientos_api'),
    path(
        'mantenimientos/<int:pk>/',
        views.mantenimiento_detalle_api,
        name='mantenimiento_detalle_api',
    ),
]

