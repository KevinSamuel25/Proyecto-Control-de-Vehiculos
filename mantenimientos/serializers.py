from rest_framework import serializers
from .models import Mantenimiento

class MantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mantenimiento
        fields = '__all__'

    def validate(self, value):
        vehiculo = value.get('vehiculo')
        km_objetivo = value.get('kilometraje_objetivo')

        if vehiculo and km_objetivo is not None:
            if km_objetivo <= vehiculo.kilometraje:
                raise serializers.ValidationError({
                    "kilometraje_objetivo": f"El kilometraje ({km_objetivo} km) debe ser mayor al actual del vehículo ({vehiculo.kilometraje} km)."
                })
        return value