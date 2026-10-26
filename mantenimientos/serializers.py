from rest_framework import serializers
from .models import Mantenimiento

class MantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mantenimiento
        fields = [
            'id',
            'vehiculo',
            'descripcion',
            'kilometraje_objetivo',
            'fecha_programada',
            'estado',
            'creado_en',
        ]
        read_only_fields = ['id', 'creado_en']

    def validate(self, attrs):
        vehiculo = attrs.get('vehiculo', self.instance.vehiculo if self.instance else None)
        km_objetivo = attrs.get(
            'kilometraje_objetivo',
            self.instance.kilometraje_objetivo if self.instance else None,
        )

        if vehiculo and km_objetivo is not None:
            if km_objetivo <= vehiculo.kilometraje:
                raise serializers.ValidationError({
                    "kilometraje_objetivo": f"El kilometraje ({km_objetivo} km) debe ser mayor al actual del vehículo ({vehiculo.kilometraje} km)."
                })
        return attrs