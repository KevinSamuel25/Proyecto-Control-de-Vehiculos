from django.db import models
from vehiculos.models import Vehiculo

class Mantenimiento(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]

    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='mantenimientos')
    descripcion = models.TextField()
    kilometraje_objetivo = models.PositiveIntegerField()
    fecha_programada = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mantenimiento {self.id} - {self.vehiculo.placa}"