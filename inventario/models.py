from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Q


class Repuesto(models.Model):
    nombre = models.CharField(max_length=120)
    codigo = models.CharField(max_length=30, unique=True)

    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=0)

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    proveedor = models.ForeignKey(
        'proveedores.Proveedor',
        on_delete=models.PROTECT,
        related_name='repuestos'
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(stock__gte=0),
                name='repuesto_stock_no_negativo'
            ),
            models.CheckConstraint(
                condition=Q(stock_minimo__gte=0),
                name='repuesto_stock_minimo_no_negativo'
            ),
            models.CheckConstraint(
                condition=Q(precio_unitario__gte=0),
                name='repuesto_precio_no_negativo'
            )
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'