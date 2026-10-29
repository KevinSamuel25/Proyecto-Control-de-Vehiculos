from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Control_de_vehiculos.seguridad import requiere_admin
from .models import Vehiculo
from .serializers import VehiculoSerializer


def _pagina(consulta, clase_serializador, numero_pagina):
    paginador = Paginator(consulta, 10)
    pagina = paginador.get_page(numero_pagina)
    return Response({
        'pagina_actual': pagina.number,
        'total_paginas': paginador.num_pages,
        'total_registros': paginador.count,
        'resultados': clase_serializador(pagina.object_list, many=True).data,
    })


def _filtro_entero(valor, nombre):
    try:
        entero = int(valor)
    except (TypeError, ValueError):
        raise ValueError(f'El filtro {nombre} debe ser un entero.')
    if entero < 0:
        raise ValueError(f'El filtro {nombre} no puede ser negativo.')
    return entero


@api_view(['GET', 'POST'])
def vehiculos_api(peticion):
    if peticion.method == 'GET':
        vehiculos = Vehiculo.objects.all().order_by('placa')
        estado = peticion.query_params.get('estado')
        kilometraje_min = peticion.query_params.get('kilometraje_min')
        kilometraje_max = peticion.query_params.get('kilometraje_max')

        if estado:
            vehiculos = vehiculos.filter(estado__iexact=estado)
        if kilometraje_min is not None:
            try:
                kilometraje_min = _filtro_entero(kilometraje_min, 'kilometraje_min')
            except ValueError as error:
                return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
            vehiculos = vehiculos.filter(kilometraje__gte=kilometraje_min)
        if kilometraje_max is not None:
            try:
                kilometraje_max = _filtro_entero(kilometraje_max, 'kilometraje_max')
            except ValueError as error:
                return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
            vehiculos = vehiculos.filter(kilometraje__lte=kilometraje_max)
        if (
            kilometraje_min is not None
            and kilometraje_max is not None
            and kilometraje_min > kilometraje_max
        ):
            return Response(
                {'error': 'kilometraje_min no puede ser mayor que kilometraje_max.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return _pagina(vehiculos, VehiculoSerializer, peticion.query_params.get('page', 1))

    error = requiere_admin(peticion)
    if error is not None:
        return error

    serializador = VehiculoSerializer(data=peticion.data)
    if serializador.is_valid():
        serializador.save()
        return Response(serializador.data, status=status.HTTP_201_CREATED)
    return Response(serializador.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def vehiculo_detalle_api(peticion, pk):
    try:
        vehiculo = Vehiculo.objects.get(pk=pk)
    except Vehiculo.DoesNotExist:
        return Response(
            {'error': 'Vehículo no encontrado.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if peticion.method == 'GET':
        return Response(VehiculoSerializer(vehiculo).data)

    error = requiere_admin(peticion)
    if error is not None:
        return error

    if peticion.method in ['PUT', 'PATCH']:
        serializador = VehiculoSerializer(
            vehiculo,
            data=peticion.data,
            partial=peticion.method == 'PATCH',
        )
        if serializador.is_valid():
            serializador.save()
            return Response(serializador.data)
        return Response(serializador.errors, status=status.HTTP_400_BAD_REQUEST)

    vehiculo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
