from django.contrib import admin
from .models import Administrador, Vivienda, HorarioVisita

class HorarioVisitaInline(admin.TabularInline):
    """
    Permite editar los horarios de visita directamente en la vista de la vivienda.
    """
    model = HorarioVisita
    extra = 1 # Muestra un formulario extra para añadir un nuevo horario.

@admin.register(Vivienda)
class ViviendaAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo Vivienda.
    """
    list_display = ('nombre', 'direccion_completa', 'referencia_catastral', 'precio_mensualidad')
    search_fields = ('nombre', 'referencia_catastral', 'direccion_completa')
    filter_horizontal = ('administradores',)
    inlines = [HorarioVisitaInline]

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo Administrador.
    """
    list_display = ('nombre', 'email', 'telefono')
    search_fields = ('nombre', 'email')

# No es estrictamente necesario registrar HorarioVisita aquí si solo se gestiona
# a través de Vivienda, pero lo hacemos para permitir la gestión directa si fuera necesario.
admin.site.register(HorarioVisita)
