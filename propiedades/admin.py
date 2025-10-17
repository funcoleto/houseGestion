from django.contrib import admin
from .models import Administrador, Vivienda, HorarioVisita, ArrendatarioAutorizado, Visita

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

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo Visita.
    """
    list_display = ('vivienda', 'nombre', 'apellidos', 'fecha_hora', 'estado', 'veces_cancelada')
    list_filter = ('estado', 'vivienda', 'fecha_hora')
    search_fields = ('nombre', 'apellidos', 'email', 'telefono', 'vivienda__nombre')
    list_per_page = 25

    # Hacemos que los campos de solo lectura se muestren en el panel de detalle.
    readonly_fields = ('cancelacion_token', 'creado_en', 'actualizado_en')

    def delete_queryset(self, request, queryset):
        """
        Sobrescribe la acción de borrado para enviar notificaciones por email.
        """
        for visita in queryset:
            # Solo enviamos email si la visita estaba confirmada
            if visita.estado == 'CONFIRMADA':
                asunto = f"Cancelación de tu visita para {visita.vivienda.nombre}"
                contexto_email = {'visita': visita}
                cuerpo_mensaje = render_to_string('propiedades/emails/cancelacion_por_admin.txt', contexto_email)

                try:
                    enviado = send_mail(asunto, cuerpo_mensaje, settings.DEFAULT_FROM_EMAIL, [visita.email])
                    if enviado:
                        print(f"Notificación de cancelación por admin enviada con éxito a {visita.email}.")
                    else:
                        print(f"ERROR: No se pudo enviar la notificación de cancelación por admin a {visita.email}.")
                except Exception as e:
                    print(f"ERROR al enviar notificación de cancelación por admin: {e}")

        # Llamamos al método original para que se realice el borrado
        super().delete_queryset(request, queryset)
