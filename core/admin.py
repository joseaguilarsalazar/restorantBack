from django.contrib import admin
from . models import (
    Empleado,
    Plato,
    Insumo,
    Mesa,
    Rol,
    Pedido,
    PlatoInsumo,
    CompraInsumo,
)

admin.site.register(Empleado)
admin.site.register(Plato)
admin.site.register(Insumo)
admin.site.register(Mesa)
admin.site.register(Rol)
admin.site.register(Pedido)
admin.site.register(PlatoInsumo)
admin.site.register(CompraInsumo)