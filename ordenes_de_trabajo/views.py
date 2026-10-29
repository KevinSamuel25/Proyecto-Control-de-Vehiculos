from django.core.paginator import Paginator
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Control_de_vehiculos.seguridad import requiere_admin, requiere_operador
from .models import OrdenTrabajo, ComentarioOrden
from .serializers import OrdenTrabajoSerializer, ComentarioOrdenSerializer


def respuesta_paginada(consulta, clase_serializador, numero_pagina):
    paginador = Paginator(consulta, 5)
    pagina = paginador.get_page(numero_pagina)
    serializador = clase_serializador(pagina.object_list, many=True)
    return Response({
        'pagina_actual': pagina.number,
        'total_paginas': paginador.num_pages,
        'total_registros': paginador.count,
        'resultados': serializador.data
    })


@api_view(['GET', 'POST'])
def ordenes_api(peticion):
    if peticion.method == 'GET':
        ordenes = OrdenTrabajo.objects.select_related('vehiculo').order_by(
            '-fecha_ingreso'
        )
        estado = peticion.query_params.get('estado')
        vehiculo = peticion.query_params.get('vehiculo')
        buscar = peticion.query_params.get('buscar')

        if estado:
            ordenes = ordenes.filter(estado__iexact=estado)
        if vehiculo:
            ordenes = ordenes.filter(vehiculo_id=vehiculo)
        if buscar:
            ordenes = ordenes.filter(
                Q(codigo__icontains=buscar) |
                Q(descripcion_falla__icontains=buscar)
            )

        return respuesta_paginada(
            ordenes, OrdenTrabajoSerializer,
            peticion.query_params.get('page', 1)
        )

    error = requiere_operador(peticion)
    if error is not None:
        return error

    serializador = OrdenTrabajoSerializer(data=peticion.data)
    if serializador.is_valid():
        serializador.save()
        return Response(serializador.data, status=status.HTTP_201_CREATED)
    return Response(serializador.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def orden_detalle_api(peticion, id):
    try:
        orden = OrdenTrabajo.objects.get(id=id)
    except OrdenTrabajo.DoesNotExist:
        return Response(
            {'error': 'Orden de trabajo no encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if peticion.method == 'GET':
        return Response(OrdenTrabajoSerializer(orden).data)

    if peticion.method == 'DELETE':
        error = requiere_admin(peticion)
        if error is not None:
            return error
        orden.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    error = requiere_operador(peticion)
    if error is not None:
        return error

    serializador = OrdenTrabajoSerializer(
        orden, data=peticion.data,
        partial=peticion.method == 'PATCH'
    )
    if serializador.is_valid():
        serializador.save()
        return Response(serializador.data)
    return Response(serializador.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def comentarios_api(peticion):
    if peticion.method == 'GET':
        comentarios = ComentarioOrden.objects.select_related(
            'orden_trabajo', 'repuesto'
        ).order_by('-orden_trabajo__fecha_ingreso')
        orden_id = peticion.query_params.get('orden')

        if orden_id:
            comentarios = comentarios.filter(orden_trabajo_id=orden_id)

        return respuesta_paginada(
            comentarios, ComentarioOrdenSerializer,
            peticion.query_params.get('page', 1)
        )

    error = requiere_operador(peticion)
    if error is not None:
        return error

    serializador = ComentarioOrdenSerializer(data=peticion.data)
    if serializador.is_valid():
        serializador.save()
        return Response(serializador.data, status=status.HTTP_201_CREATED)
    return Response(serializador.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
def comentario_detalle_api(peticion, pk):
    try:
        comentario = ComentarioOrden.objects.get(pk=pk)
    except ComentarioOrden.DoesNotExist:
        return Response(
            {'error': 'Comentario no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if peticion.method == 'GET':
        return Response(ComentarioOrdenSerializer(comentario).data)

    error = requiere_admin(peticion)
    if error is not None:
        return error
    comentario.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
