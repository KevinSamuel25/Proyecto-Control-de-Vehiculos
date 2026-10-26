from django.contrib import admin

from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'marca', 'modelo', 'kilometraje', 'estado')
    list_filter = ('estado',)
    search_fields = ('placa', 'marca', 'modelo')
