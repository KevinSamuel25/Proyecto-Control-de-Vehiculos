from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

class Vehiculo(models.Model):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('EN_TALLER', 'En Taller'),
        ('INACTIVO', 'Inactivo'),
    ]

    placa = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9-]{3,15}$',
                message='La placa debe contener entre 3 y 15 caracteres letras, numeros o guiones.',
            )
        ],
    )
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.PositiveIntegerField()
    kilometraje = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO')
    creado_en = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.placa = self.placa.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.marca} - {self.modelo} - ({self.placa})"