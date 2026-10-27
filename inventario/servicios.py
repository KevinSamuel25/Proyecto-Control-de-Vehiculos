from django.db import transaction
from django.db.models import F

from rest_framework.exceptions import ValidationError, NotFound

from .models import Repuesto


@transaction.atomic
def registrar_consumo(orden_id, repuesto_id, cantidad):

    from ordenes_de_trabajo.models import OrdenTrabajo, ComentarioOrden

    try:
        orden = OrdenTrabajo.objects.select_for_update().get(pk=orden_id)
    except OrdenTrabajo.DoesNotExist:
        raise NotFound('Orden de trabajo no encontrada.')

    if orden.estado not in ['ABIERTA', 'EN_PROCESO']:
        raise ValidationError({
            'orden': 'Solo se pueden agregar repuestos a ordenes activas.'
        })

    try:
        repuesto = Repuesto.objects.get(pk=repuesto_id)
    except Repuesto.DoesNotExist:
        raise NotFound('Repuesto no encontrado.')

    actualizados = Repuesto.objects.filter(
        pk=repuesto_id,
        stock__gte=cantidad
    ).update(
        stock=F('stock') - cantidad
    )

    if actualizados == 0:
        raise ValidationError({
            'cantidad': 'Stock insuficiente para realizar el consumo.'
        })

    detalle = ComentarioOrden.objects.create(
        orden_trabajo=orden,
        repuesto=repuesto,
        cantidad_utilizada=cantidad,
        precio_unitario_aplicado=repuesto.precio_unitario
    )

    OrdenTrabajo.objects.filter(pk=orden_id).update(
        costo_total=F('costo_total') + repuesto.precio_unitario * cantidad
    )

    return detalle