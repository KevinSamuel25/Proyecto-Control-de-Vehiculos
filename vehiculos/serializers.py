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

    def validate_placa(self, valor):
        return valor.strip().upper()

    def to_internal_value(self, datos):
        datos_normalizados = datos.copy()
        if 'placa' in datos_normalizados and datos_normalizados['placa'] is not None:
            datos_normalizados['placa'] = datos_normalizados['placa'].strip().upper()
        return super().to_internal_value(datos_normalizados)
