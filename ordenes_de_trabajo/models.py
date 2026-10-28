from django.db import models

from django.db import models
from django.contrib.auth.models import User
from vehiculos.models import Vehiculo
from inventario.models import Repuesto

class OrdenTrabajo(models.Model):
    """
    Modelo principal para registrar las incidencias y órdenes de trabajo
    """
    ESTADOS = [
        ('ABIERTA', 'Abierta'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    codigo = models.CharField(max_length=20, unique=True, editable=False)
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.PROTECT,
        related_name='ordenes_trabajo'
    )
    mecanico = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='ordenes_asignadas'
    )
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_salida = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20,choices=ESTADOS,default='ABIERTA')
    descripcion_falla = models.TextField()
    costo_total = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)

    def __str__(self):
        return f"{self.codigo} - {self.vehiculo.placa}"


class ComentarioOrden(models.Model):
    """
    Permite llevar una bitácora o historial de avances y notas sobre la orden de trabajo
    """
    orden_trabajo = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    # Asumimos que Integrante 3 definió el modelo Repuesto en la app 'inventario'
    repuesto = models.ForeignKey(
        Repuesto,
        on_delete=models.PROTECT,
        related_name='comentarios_ordenes'
)
    cantidad_utilizada = models.PositiveIntegerField(default=1)
    precio_unitario_aplicado = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.cantidad_utilizada} - {self.orden_trabajo.codigo}"