from rest_framework import serializers
from .models import Repuesto


class RepuestoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Repuesto
        fields = '__all__'


class ConsumoRepuestoSerializer(serializers.Serializer):
    orden = serializers.IntegerField(min_value=1)
    repuesto = serializers.IntegerField(min_value=1)
    cantidad = serializers.IntegerField(min_value=1)