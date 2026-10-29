from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Control_de_vehiculos.seguridad import requiere_admin
from .models import Mantenimiento
from .serializers import MantenimientoSerializer


def _pagina(consulta, numero_pagina):
    paginador = Paginator(consulta, 10)
    pagina = paginador.get_page(numero_pagina)
    return Response({
        'pagina_actual': pagina.number,
        'total_paginas': paginador.num_pages,
        'total_registros': paginador.count,
        'resultados': MantenimientoSerializer(pagina.object_list, many=True).data,
    })


@api_view(['GET', 'POST'])
def mantenimientos_api(peticion):
    if peticion.method == 'GET':
        mantenimientos = Mantenimiento.objects.select_related('vehiculo').order_by(
            'kilometraje_objetivo'
        )
        estado = peticion.query_params.get('estado')
        vehiculo_id = peticion.query_params.get('vehiculo')
        if estado:
            mantenimientos = mantenimientos.filter(estado__iexact=estado)
        if vehiculo_id:
            mantenimientos = mantenimientos.filter(vehiculo_id=vehiculo_id)
        return _pagina(mantenimientos, peticion.query_params.get('page', 1))

    error = requiere_admin(peticion)
    if error is not None:
        return error

    serializador = MantenimientoSerializer(data=peticion.data)
    if serializador.is_valid():
        serializador.save()
        return Response(serializador.data, status=status.HTTP_201_CREATED)
    return Response(serializador.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def mantenimiento_detalle_api(peticion, pk):
    try:
        mantenimiento = Mantenimiento.objects.select_related('vehiculo').get(pk=pk)
    except Mantenimiento.DoesNotExist:
        return Response(
            {'error': 'Mantenimiento no encontrado.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if peticion.method == 'GET':
        return Response(MantenimientoSerializer(mantenimiento).data)

    error = requiere_admin(peticion)
    if error is not None:
        return error

    if peticion.method in ['PUT', 'PATCH']:
        serializador = MantenimientoSerializer(
            mantenimiento,
            data=peticion.data,
            partial=peticion.method == 'PATCH',
        )
        if serializador.is_valid():
            serializador.save()
            return Response(serializador.data)
        return Response(serializador.errors, status=status.HTTP_400_BAD_REQUEST)

    mantenimiento.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
