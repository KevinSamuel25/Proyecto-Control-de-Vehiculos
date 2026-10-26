from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Mantenimiento
from .serializers import MantenimientoSerializer


def _pagina(queryset, page_number):
    paginator = Paginator(queryset, 10)
    page = paginator.get_page(page_number)
    return Response({
        'pagina_actual': page.number,
        'total_paginas': paginator.num_pages,
        'total_registros': paginator.count,
        'resultados': MantenimientoSerializer(page.object_list, many=True).data,
    })


def _requiere_staff(request):
    return request.user.is_authenticated and request.user.is_staff


@api_view(['GET', 'POST'])
def mantenimientos_api(request):
    if request.method == 'GET':
        mantenimientos = Mantenimiento.objects.select_related('vehiculo').order_by(
            'kilometraje_objetivo'
        )
        estado = request.query_params.get('estado')
        vehiculo_id = request.query_params.get('vehiculo')
        if estado:
            mantenimientos = mantenimientos.filter(estado__iexact=estado)
        if vehiculo_id:
            mantenimientos = mantenimientos.filter(vehiculo_id=vehiculo_id)
        return _pagina(mantenimientos, request.query_params.get('page', 1))

    if not _requiere_staff(request):
        return Response(
            {'error': 'Se requiere un usuario administrador.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = MantenimientoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def mantenimiento_detalle_api(request, pk):
    try:
        mantenimiento = Mantenimiento.objects.select_related('vehiculo').get(pk=pk)
    except Mantenimiento.DoesNotExist:
        return Response(
            {'error': 'Mantenimiento no encontrado.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        return Response(MantenimientoSerializer(mantenimiento).data)

    if not _requiere_staff(request):
        return Response(
            {'error': 'Se requiere un usuario administrador.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method in ['PUT', 'PATCH']:
        serializer = MantenimientoSerializer(
            mantenimiento,
            data=request.data,
            partial=request.method == 'PATCH',
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    mantenimiento.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
