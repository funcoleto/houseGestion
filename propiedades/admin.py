from django.contrib import admin
from .models import Administrador, Vivienda, HorarioVisita, ArrendatarioAutorizado, Visita, SolicitudSeguro

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

from django.core.mail import EmailMultiAlternatives
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
    actions = ['cancelar_por_alquiler', 'cancelar_por_otro_motivo']

    # Hacemos que los campos de solo lectura se muestren en el panel de detalle.
    readonly_fields = ('cancelacion_token', 'creado_en', 'actualizado_en', 'motivo_cancelacion')

    def get_actions(self, request):
        """
        Desactiva la acción de borrado por defecto ('delete_selected').
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def _cancelar_visitas(self, request, queryset, motivo):
        """
        Lógica interna para cancelar visitas y enviar notificaciones.
        """
        for visita in queryset:
            if visita.estado == 'CONFIRMADA':
                visita.estado = 'CANCELADA'
                visita.motivo_cancelacion = motivo
                visita.veces_cancelada += 1
                visita.save()

                # Enviar notificación por email
                asunto = f"Cancelación de tu visita para {visita.vivienda.nombre}"
                contexto_email = {'visita': visita}
                cuerpo_mensaje = render_to_string('propiedades/emails/cancelacion_por_admin.txt', contexto_email)
                html_cuerpo_mensaje = render_to_string('propiedades/emails/cancelacion_por_admin.html', contexto_email)

                try:
                    msg = EmailMultiAlternatives(asunto, cuerpo_mensaje, settings.DEFAULT_FROM_EMAIL, [visita.email])
                    msg.attach_alternative(html_cuerpo_mensaje, "text/html")
                    msg.send()
                    print(f"Notificación de cancelación (motivo: {motivo}) enviada a {visita.email}.")
                except Exception as e:
                    print(f"ERROR al enviar notificación de cancelación: {e}")

        self.message_user(request, f"{queryset.count()} visitas han sido canceladas exitosamente.")

    @admin.action(description="Cancelar seleccionadas (Vivienda ya alquilada)")
    def cancelar_por_alquiler(self, request, queryset):
        self._cancelar_visitas(request, queryset, "La vivienda para la que solicitó la visita ya ha sido alquilada.")

    @admin.action(description="Cancelar seleccionadas (Otro motivo)")
    def cancelar_por_otro_motivo(self, request, queryset):
        self._cancelar_visitas(request, queryset, "La visita ha sido cancelada por el administrador por otros motivos.")

    @admin.action(description="Iniciar proceso de seguro para el candidato")
    def iniciar_proceso_seguro(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(request, "Por favor, selecciona solo un candidato a la vez para iniciar el proceso.", level='error')
            return

        visita = queryset.first()
        if hasattr(visita, 'solicitud_seguro'):
            self.message_user(request, f"El candidato {visita.nombre} ya tiene una solicitud de seguro en proceso.", level='warning')
            return

        solicitud = SolicitudSeguro.objects.create(visita=visita)

        # Enviar email al candidato
        asunto = f"Siguientes pasos para el alquiler de {visita.vivienda.nombre}"
        enlace_subida = request.build_absolute_uri(
            reverse('propiedades:subir_documentos_seguro', args=[solicitud.token_acceso])
        )
        contexto_email = {'visita': visita, 'enlace_subida': enlace_subida}

        cuerpo_mensaje = render_to_string('propiedades/emails/instrucciones_seguro.txt', contexto_email)
        html_cuerpo_mensaje = render_to_string('propiedades/emails/instrucciones_seguro.html', contexto_email)

        try:
            msg = EmailMultiAlternatives(asunto, cuerpo_mensaje, settings.DEFAULT_FROM_EMAIL, [visita.email])
            msg.attach_alternative(html_cuerpo_mensaje, "text/html")
            msg.send()
            self.message_user(request, f"Se ha enviado un correo con instrucciones a {visita.nombre}.")
            print(f"Correo de inicio de proceso de seguro enviado a {visita.email}.")
        except Exception as e:
            self.message_user(request, f"No se pudo enviar el correo a {visita.nombre}. Error: {e}", level='error')
            print(f"ERROR al enviar correo de inicio de proceso de seguro: {e}")

@admin.register(SolicitudSeguro)
class SolicitudSeguroAdmin(admin.ModelAdmin):
    list_display = ('visita', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    readonly_fields = ('token_acceso',)
