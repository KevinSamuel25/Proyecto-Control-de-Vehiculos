from django.shortcuts import render

from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import EquipoArena, OrdenTrabajo, ComentarioOrden
from .serializers import (
    EquipoArenaSerializer,
    OrdenTrabajoSerializer,
    ComentarioOrdenSerializer
)

# Función para la paginación de los listados
def respuesta_paginada(queryset, serializer_class, page_number):
    paginator = Paginator(queryset, 5)
    page = paginator.get_page(page_number)
    serializer = serializer_class(page.object_list, many=True)
    return Response({
        'pagina_actual': page.number,
        'total_paginas': paginator.num_pages,
        'total_registros': paginator.count,
        'resultados': serializer.data
    })

# =====================================================================
# VISTAS PARA EQUIPOS DE ARENA
# =====================================================================

@api_view(['GET', 'POST'])
def equipos_api(request):
    if request.method == 'GET':
        equipos = EquipoArena.objects.order_by('codigo')
        tipo = request.query_params.get('tipo')
        activo = request.query_params.get('activo')
        buscar = request.query_params.get('buscar')

        if tipo:
            equipos = equipos.filter(tipo__iexact=tipo)
        if activo is not None:
            if activo.lower() not in ['true', 'false']:
                return Response(
                    {'error': 'Utilice true o false.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            equipos = equipos.filter(activo=activo.lower() == 'true')
        if buscar:
            equipos = equipos.filter(nombre__icontains=buscar)

        return respuesta_paginada(
            equipos, EquipoArenaSerializer,
            request.query_params.get('page', 1)
        )

    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({'error': 'Se requiere administrador.'}, status=403)

    serializer = EquipoArenaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def equipo_detalle_api(request, id):
    try:
        equipo = EquipoArena.objects.get(id=id)
    except EquipoArena.DoesNotExist:
        return Response({'error': 'Equipo no encontrado.'}, status=404)

    if request.method == 'GET':
        return Response(EquipoArenaSerializer(equipo).data)

    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({'error': 'Se requiere administrador.'}, status=403)

    if request.method in ['PUT', 'PATCH']:
        serializer = EquipoArenaSerializer(
            equipo, data=request.data,
            partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    equipo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# VISTAS PARA ÓRDENES DE TRABAJO
# =====================================================================

@api_view(['GET', 'POST'])
def ordenes_api(request):
    if request.method == 'GET':
        ordenes = OrdenTrabajo.objects.order_by('-fecha_creacion')
        estado = request.query_params.get('estado')
        prioridad = request.query_params.get('prioridad')
        buscar = request.query_params.get('buscar')

        if estado:
            ordenes = ordenes.filter(estado__iexact=estado)
        if prioridad:
            ordenes = ordenes.filter(prioridad__iexact=prioridad)
        if buscar:
            ordenes = ordenes.filter(titulo__icontains=buscar)

        return respuesta_paginada(
            ordenes, OrdenTrabajoSerializer,
            request.query_params.get('page', 1)
        )

    if not request.user.is_authenticated:
        return Response({'error': 'Autenticación requerida.'}, status=401)

    serializer = OrdenTrabajoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def orden_detalle_api(request, id):
    try:
        orden = OrdenTrabajo.objects.get(id=id)
    except OrdenTrabajo.DoesNotExist:
        return Response({'error': 'Orden de trabajo no encontrada.'}, status=404)

    if request.method == 'GET':
        return Response(OrdenTrabajoSerializer(orden).data)

    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({'error': 'Se requiere administrador.'}, status=403)

    if request.method in ['PUT', 'PATCH']:
        serializer = OrdenTrabajoSerializer(
            orden, data=request.data,
            partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    orden.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# VISTAS PARA COMENTARIOS DE ÓRDENES
# =====================================================================

@api_view(['GET', 'POST'])
def comentarios_api(request):
    if request.method == 'GET':
        comentarios = ComentarioOrden.objects.order_by('-fecha_creacion')
        orden_id = request.query_params.get('orden')
        
        if orden_id:
            comentarios = comentarios.filter(orden_id=orden_id)
            
        return respuesta_paginada(
            comentarios, ComentarioOrdenSerializer,
            request.query_params.get('page', 1)
        )

    if not request.user.is_authenticated:
        return Response({'autenticación': 'Autenticación requerida.'}, status=401)

    serializer = ComentarioOrdenSerializer(data=request.data)
    if serializer.is_valid():

        serializer.save(autor=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)