from rest_framework import serializers

from .models import OrdenTrabajo, ComentarioOrden


class ComentarioOrdenSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = ComentarioOrden
        fields = [
            'id',
            'orden_trabajo',
            'repuesto',
            'cantidad_utilizada',
            'precio_unitario_aplicado',
            'subtotal',
        ]


class OrdenTrabajoSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrdenTrabajo
        fields = [
            'id',
            'codigo',
            'vehiculo',
            'mecanico',
            'fecha_ingreso',
            'fecha_salida',
            'estado',
            'descripcion_falla',
            'costo_total',
        ]
        read_only_fields = ['id', 'codigo', 'fecha_ingreso']

    def validate_vehiculo(self, valor):
        if self.instance is None:
            tiene_activa = OrdenTrabajo.objects.filter(
                vehiculo=valor,
                estado__in=OrdenTrabajo.ESTADOS_ACTIVOS,
            ).exists()
            if tiene_activa:
                raise serializers.ValidationError(
                    'El vehículo ya tiene una orden de trabajo activa (ABIERTA o EN_PROCESO).'
                )
        return valor

    def validate(self, datos):
        if self.instance is not None and (
            self.instance.estado in OrdenTrabajo.ESTADOS_CERRADOS
        ):
            raise serializers.ValidationError(
                'No se puede modificar una orden COMPLETADA o CANCELADA.'
            )

        estado = datos.get(
            'estado', self.instance.estado if self.instance else None
        )
        fecha_ingreso = (
            self.instance.fecha_ingreso if self.instance else None
        )
        fecha_salida = datos.get(
            'fecha_salida',
            self.instance.fecha_salida if self.instance else None,
        )
        costo_total = datos.get(
            'costo_total',
            self.instance.costo_total if self.instance else None,
        )

        if estado == 'COMPLETADA' and not fecha_salida:
            raise serializers.ValidationError({
                'fecha_salida': 'Debe registrar la fecha de salida al completar la orden.'
            })

        if fecha_salida and fecha_ingreso and fecha_salida < fecha_ingreso:
            raise serializers.ValidationError({
                'fecha_salida': 'La fecha de salida no puede ser anterior a la fecha de ingreso.'
            })

        if costo_total is not None and costo_total < 0:
            raise serializers.ValidationError({
                'costo_total': 'El costo total no puede ser un valor negativo.'
            })

        return datos
