from django.core.paginator import Paginator
from django.db.models import F, Q, Sum, Count, DecimalField
from django.db.models.deletion import ProtectedError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Control_de_vehiculos.seguridad import requiere_admin, requiere_operador
from .models import Repuesto
from .serializers import RepuestoSerializer, ConsumoRepuestoSerializer
from .servicios import registrar_consumo


@api_view(['GET', 'POST'])
def inventario_api(peticion):

    if peticion.method == 'GET':
        repuestos = Repuesto.objects.select_related('proveedor').order_by('id')

        buscar = peticion.query_params.get('buscar')
        proveedor = peticion.query_params.get('proveedor')
        bajo_stock = peticion.query_params.get('bajo_stock')
        ordenar = peticion.query_params.get('ordenar', 'id')

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

        paginador = Paginator(repuestos, 5)
        pagina = paginador.get_page(peticion.query_params.get('page', 1))

        serializador = RepuestoSerializer(pagina.object_list, many=True)

        return Response({
            'pagina_actual': pagina.number,
            'total_paginas': paginador.num_pages,
            'total_registros': pagina.paginator.count,
            'resultados': serializador.data
        })

    error = requiere_admin(peticion)
    if error is not None:
        return error

    serializador = RepuestoSerializer(data=peticion.data)

    if serializador.is_valid():
        serializador.save()
        return Response(
            serializador.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializador.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def repuesto_detalle_api(peticion, pk):

    try:
        repuesto = Repuesto.objects.get(pk=pk)
    except Repuesto.DoesNotExist:
        return Response(
            {'error': 'Repuesto no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if peticion.method == 'GET':
        serializador = RepuestoSerializer(repuesto)
        return Response(serializador.data)

    error = requiere_admin(peticion)
    if error is not None:
        return error

    if peticion.method in ['PUT', 'PATCH']:

        serializador = RepuestoSerializer(
            repuesto,
            data=peticion.data,
            partial=peticion.method == 'PATCH'
        )

        if serializador.is_valid():
            serializador.save()
            return Response(serializador.data)

        return Response(
            serializador.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if peticion.method == 'DELETE':
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
def resumen_inventario_api(peticion):

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
def consumo_repuesto_api(peticion):

    error = requiere_operador(peticion)
    if error is not None:
        return error

    serializador = ConsumoRepuestoSerializer(data=peticion.data)

    if not serializador.is_valid():
        return Response(
            serializador.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    detalle = registrar_consumo(
        orden_id=serializador.validated_data['orden'],
        repuesto_id=serializador.validated_data['repuesto'],
        cantidad=serializador.validated_data['cantidad']
    )

    return Response({
        'mensaje': 'Repuesto agregado a la orden y descontado del inventario.',
        'detalle_id': detalle.id,
        'cantidad_utilizada': detalle.cantidad_utilizada
    }, status=status.HTTP_201_CREATED)
