from django.db import models
from django.core.exceptions import ValidationError
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

    def clean(self):
        if (
            self.vehiculo_id
            and self.kilometraje_objetivo is not None
            and self.kilometraje_objetivo <= self.vehiculo.kilometraje
        ):
            raise ValidationError({
                'kilometraje_objetivo': (
                    'El kilometraje objetivo debe ser mayor al kilometraje actual '
                    'del vehículo.'
                )
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Mantenimiento {self.id} - {self.vehiculo.placa}"