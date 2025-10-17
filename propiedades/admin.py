from django.contrib import admin
from .models import Administrador, Vivienda, HorarioVisita, ArrendatarioAutorizado

class HorarioVisitaInline(admin.TabularInline):
    """
    Permite editar los horarios de visita directamente en la vista de la vivienda.
    """
    model = HorarioVisita
    extra = 1 # Muestra un formulario extra para añadir un nuevo horario.
    ordering = ('fecha', 'hora_inicio')

class ArrendatarioAutorizadoInline(admin.TabularInline):
    """
    Permite editar los arrendatarios autorizados directamente en la vista de la vivienda.
    """
    model = ArrendatarioAutorizado
    extra = 1 # Muestra un formulario extra.

@admin.register(Vivienda)
class ViviendaAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo Vivienda.
    """
    list_display = ('nombre', 'direccion_completa', 'referencia_catastral', 'precio_mensualidad')
    search_fields = ('nombre', 'referencia_catastral', 'direccion_completa')
    filter_horizontal = ('administradores',)
    inlines = [
        ArrendatarioAutorizadoInline,
        HorarioVisitaInline,
    ]

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo Administrador.
    """
    list_display = ('nombre', 'email', 'telefono')
    search_fields = ('nombre', 'email')

# Registramos los otros modelos para que también se puedan gestionar de forma independiente.
@admin.register(HorarioVisita)
class HorarioVisitaAdmin(admin.ModelAdmin):
    list_display = ('vivienda', 'fecha', 'hora_inicio', 'hora_fin')
    list_filter = ('vivienda', 'fecha')

@admin.register(ArrendatarioAutorizado)
class ArrendatarioAutorizadoAdmin(admin.ModelAdmin):
    list_display = ('vivienda', 'telefono')
    list_filter = ('vivienda',)
    search_fields = ('telefono',)
