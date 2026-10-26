from rest_framework import serializers

from .models import Vehiculo


class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = [
            'id',
            'placa',
            'marca',
            'modelo',
            'anio',
            'kilometraje',
            'estado',
            'creado_en',
        ]
        read_only_fields = ['id', 'creado_en']

    def validate_placa(self, value):
        return value.strip().upper()

    def to_internal_value(self, data):
        normalized_data = data.copy()
        if 'placa' in normalized_data and normalized_data['placa'] is not None:
            normalized_data['placa'] = normalized_data['placa'].strip().upper()
        return super().to_internal_value(normalized_data)
