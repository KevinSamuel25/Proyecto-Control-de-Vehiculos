from django.db import models

from django.db import models
from django.contrib.auth.models import User


class OrdenTrabajo(models.Model):
    """
    Modelo principal para registrar las incidencias y órdenes de trabajo
    """
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('RESUELTA', 'Resuelta'),
        ('CANCELADA', 'Cancelada'),
    ]

    PRIORIDADES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='MEDIA')

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    costo_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    costo_real = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.id} - {self.titulo}"


class ComentarioOrden(models.Model):
    """
    Permite llevar una bitácora o historial de avances y notas sobre la orden de trabajo
    """
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.autor.username} - {self.orden.id}"