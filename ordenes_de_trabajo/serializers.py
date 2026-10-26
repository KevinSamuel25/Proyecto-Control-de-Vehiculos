from rest_framework import serializers
from .models import OrdenTrabajo, ComentarioOrden


class OrdenTrabajoSerializer(serializers.ModelSerializer):
    equipo_nombre = serializers.CharField(source='equipo.nombre', read_only=True)

    class Meta:
        model = OrdenTrabajo
        fields = [
            'id', 
            'titulo', 
            'descripcion', 
            'estado', 
            'prioridad', 
            'fecha_creacion', 
            'fecha_actualizacion', 
            'fecha_resolucion', 
            'costo_estimado', 
            'costo_real'
        ]

    def validate(self, data):

        estado = data.get('estado', self.instance.estado if self.instance else None)
        fecha_resolucion = data.get('fecha_resolucion', self.instance.fecha_resolucion if self.instance else None)
        costo_estimado = data.get('costo_estimado', self.instance.costo_estimado if self.instance else 0)
        costo_real = data.get('costo_real', self.instance.costo_real if self.instance else 0)

        # 1. Validar que si está RESUELTA, tenga fecha de resolución
        if estado == 'RESUELTA' and not fecha_resolucion:
            raise serializers.ValidationError({
                'fecha_resolucion': 'Debe especificar una fecha de resolución cuando el estado es Resuelta.'
            })

        # 2. Validar que los costos no sean negativos
        if costo_estimado is not None and costo_estimado < 0:
            raise serializers.ValidationError({
                'costo_estimado': 'El costo estimado no puede ser un valor negativo.'
            })

        if costo_real is not None and costo_real < 0:
            raise serializers.ValidationError({
                'costo_real': 'El costo real no puede ser un valor negativo.'
            })

        return data


class ComentarioOrdenSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComentarioOrden
        fields = [
            'id', 
            'orden', 
            'autor', 
            'texto', 
            'fecha_creacion'
        ]