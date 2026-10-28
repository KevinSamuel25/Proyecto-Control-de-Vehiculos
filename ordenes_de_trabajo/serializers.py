from rest_framework import serializers
from .models import OrdenTrabajo, ComentarioOrden


class ComentarioOrdenSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = ComentarioOrden
        fields = '__all__'


class OrdenTrabajoSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrdenTrabajo
        fields = '__all__'

    def validate_vehiculo(self, value):
        # RN-03: No permitir crear/abrir si ya tiene una orden activa (ABIERTA o EN_PROCESO)
        if not self.instance:  # Solo al crear una nueva orden
            ordenes_activas = OrdenTrabajo.objects.filter(
                vehiculo=value,
                estado__in=[OrdenTrabajo.ABIERTA, OrdenTrabajo.EN_PROCESO]
            ).exists()
            
            if ordenes_activas:
                raise serializers.ValidationError(
                    "El vehículo ya tiene una Orden de Trabajo activa (ABIERTA o EN_PROCESO)."
                )
        return value

    def validate_notificaciones(self, attrs):
        # RN-05: Impedir modificaciones si la orden está COMPLETADA o CANCELADA
        if self.instance and self.instance.estado in [OrdenTrabajo.COMPLETADA, OrdenTrabajo.CANCELADA]:
            raise serializers.ValidationError(
                "No se puede modificar una orden que ya está COMPLETADA o CANCELADA."
            )
        return attrs

    def validate(self, data):
        
        estado = data.get('estado', self.instance.estado if self.instance else None)
        fecha_ingreso = data.get('fecha_ingreso', self.instance.fecha_ingreso if self.instance else None)
        fecha_salida = data.get('fecha_salida', self.instance.fecha_salida if self.instance else None)
        costo_total = data.get('costo_total', self.instance.costo_total if self.instance else None)

        if estado == 'RESUELTA' and not fecha_salida:
            raise serializers.ValidationError({
                'fecha_salida': 'Debe especificar una fecha de salida cuando el estado es Resuelta.'
            })

        if fecha_salida and fecha_ingreso and fecha_salida < fecha_ingreso:
            raise serializers.ValidationError({
                'fecha_salida': 'La fecha de salida no puede ser anterior a la fecha de ingreso.'
            })

        if costo_total is not None and costo_total < 0:
            raise serializers.ValidationError({
                'costo_total': 'El costo total no puede ser un valor negativo.'
            })

        return data