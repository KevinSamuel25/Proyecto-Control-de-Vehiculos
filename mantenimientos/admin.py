from django.contrib import admin

from .models import Mantenimiento


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ('vehiculo', 'kilometraje_objetivo', 'fecha_programada', 'estado')
    list_filter = ('estado',)
    search_fields = ('vehiculo__placa', 'descripcion')
