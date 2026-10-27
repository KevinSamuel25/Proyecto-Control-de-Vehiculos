from django.core.paginator import Paginator
from django.db.models import F, Q, Sum, Count, DecimalField
from django.db.models.deletion import ProtectedError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Repuesto
from .serializers import RepuestoSerializer, ConsumoRepuestoSerializer
from .servicios import registrar_consumo


def verificar_admin(request):
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticacion requerida.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not request.user.is_staff:
        return Response(
            {'error': 'Se requiere administrador.'},
            status=status.HTTP_403_FORBIDDEN
        )

    return None


@api_view(['GET', 'POST'])
def inventario_api(request):

    if request.method == 'GET':
        repuestos = Repuesto.objects.select_related('proveedor').order_by('id')

        buscar = request.query_params.get('buscar')
        proveedor = request.query_params.get('proveedor')
        bajo_stock = request.query_params.get('bajo_stock')
        ordenar = request.query_params.get('ordenar', 'id')

        if buscar:
            repuestos = repuestos.filter(
                Q(nombre__icontains=buscar) |
                Q(codigo__icontains=buscar)
            )

        if proveedor:
            if not proveedor.isdecimal():
                return Response(
                    {'error': 'El proveedor debe ser un ID numerico.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            repuestos = repuestos.filter(proveedor_id=int(proveedor))

        if bajo_stock not in [None, '0', '1']:
            return Response(
                {'error': 'bajo_stock debe ser 0 o 1.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if bajo_stock == '1':
            repuestos = repuestos.filter(
                stock__lte=F('stock_minimo')
            )

        ordenamientos = [
            'id', 'nombre', 'precio_unitario',
            '-precio_unitario', 'stock', '-stock'
        ]

        if ordenar not in ordenamientos:
            return Response(
                {'error': 'Ordenamiento no valido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        repuestos = repuestos.order_by(ordenar)

        paginator = Paginator(repuestos, 5)
        pagina = paginator.get_page(request.query_params.get('page', 1))

        serializer = RepuestoSerializer(pagina.object_list, many=True)

        return Response({
            'pagina_actual': pagina.number,
            'total_paginas': paginator.num_pages,
            'total_registros': paginator.count,
            'resultados': serializer.data
        })

    error = verificar_admin(request)
    if error is not None:
        return error

    serializer = RepuestoSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def repuesto_detalle_api(request, pk):

    try:
        repuesto = Repuesto.objects.get(pk=pk)
    except Repuesto.DoesNotExist:
        return Response(
            {'error': 'Repuesto no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = RepuestoSerializer(repuesto)
        return Response(serializer.data)

    error = verificar_admin(request)
    if error is not None:
        return error

    if request.method in ['PUT', 'PATCH']:

        serializer = RepuestoSerializer(
            repuesto,
            data=request.data,
            partial=request.method == 'PATCH'
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'DELETE':
        try:
            repuesto.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        except ProtectedError:
            return Response(
                {'error': 'El repuesto tiene registros asociados y no puede eliminarse.'},
                status=status.HTTP_409_CONFLICT
            )


@api_view(['GET'])
def resumen_inventario_api(request):

    resumen = Repuesto.objects.aggregate(
        total_tipos=Count('id'),
        total_unidades=Sum('stock'),
        valor_inventario=Sum(
            F('stock') * F('precio_unitario'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    )

    return Response({
        'total_tipos': resumen['total_tipos'],
        'total_unidades': resumen['total_unidades'] or 0,
        'valor_inventario': resumen['valor_inventario'] or 0
    })


@api_view(['POST'])
def consumo_repuesto_api(request):

    error = verificar_admin(request)
    if error is not None:
        return error

    serializer = ConsumoRepuestoSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    detalle = registrar_consumo(
        orden_id=serializer.validated_data['orden'],
        repuesto_id=serializer.validated_data['repuesto'],
        cantidad=serializer.validated_data['cantidad']
    )

    return Response({
        'mensaje': 'Repuesto agregado a la orden y descontado del inventario.',
        'detalle_id': detalle.id,
        'cantidad_utilizada': detalle.cantidad_utilizada
    }, status=status.HTTP_201_CREATED)