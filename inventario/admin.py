from django.contrib import admin
from .models import Repuesto


@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'codigo',
        'nombre',
        'stock',
        'stock_minimo',
        'precio_unitario',
        'proveedor'
    )

    search_fields = ('nombre', 'codigo')
    list_filter = ('proveedor',)