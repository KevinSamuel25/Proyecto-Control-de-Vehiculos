from django.db import models

class Vehiculo(models.Model):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('EN_TALLER', 'En Taller'),
        ('INACTIVO', 'Inactivo'),
    ]

    placa = models.CharField(max_length=15, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.PositiveIntegerField()
    kilometraje = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.marca} - {self.modelo} - ({self.placa})"