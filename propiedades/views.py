from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

from .forms import AccesoArrendatarioForm, AgendarVisitaForm
from .models import ArrendatarioAutorizado, Vivienda, Visita, HorarioVisita

# --- Vistas del Flujo del Arrendatario (Proceso 1) ---

def acceso_arrendatario_view(request):
    """
    Página de acceso donde el arrendatario introduce su número de teléfono.
    """
    if request.method == 'POST':
        form = AccesoArrendatarioForm(request.POST)
        if form.is_valid():
            telefono = form.cleaned_data['telefono']

            # Primero, comprobamos si este teléfono ya tiene una visita confirmada.
            visita_activa = Visita.objects.filter(telefono=telefono, estado='CONFIRMADA').first()
            if visita_activa:
                # Si ya tiene una visita, lo redirigimos a la página de gestión.
                return redirect(reverse('propiedades:gestionar_visita', args=[visita_activa.cancelacion_token]))

            autorizaciones = ArrendatarioAutorizado.objects.filter(telefono=telefono)
            viviendas_ids = list(autorizaciones.values_list('vivienda_id', flat=True))

            if not viviendas_ids:
                form.add_error('telefono', 'Este número de teléfono no está autorizado para visitar ninguna vivienda.')
            else:
                request.session['telefono_autorizado'] = telefono
                request.session['viviendas_autorizadas_ids'] = viviendas_ids
                request.session.save()

                if len(viviendas_ids) == 1:
                    return redirect(reverse('propiedades:agendar_visita', args=[viviendas_ids[0]]))
                else:
                    return redirect(reverse('propiedades:seleccionar_vivienda'))
    else:
        form = AccesoArrendatarioForm()

    return render(request, 'propiedades/acceso_arrendatario.html', {'form': form})


def _get_horarios_disponibles(vivienda):
    """
    Calcula y devuelve una lista de tuplas con los huecos de visita disponibles.
    """
    duracion_visita = timedelta(minutes=vivienda.duracion_visita_minutos)
    # Solo consideramos horarios futuros.
    horarios_definidos = HorarioVisita.objects.filter(vivienda=vivienda, fecha__gte=timezone.now().date()).order_by('fecha', 'hora_inicio')
    visitas_confirmadas = Visita.objects.filter(vivienda=vivienda, estado='CONFIRMADA', fecha_hora__gte=timezone.now())

    # Hacemos que las fechas de las visitas confirmadas sean conscientes de la zona horaria.
    fechas_ocupadas = {v.fecha_hora for v in visitas_confirmadas}
    huecos_disponibles = []

    for horario in horarios_definidos:
        # Combinamos fecha y hora y lo hacemos consciente de la zona horaria actual de Django.
        hora_inicio_aware = timezone.make_aware(datetime.combine(horario.fecha, horario.hora_inicio))
        hora_fin_aware = timezone.make_aware(datetime.combine(horario.fecha, horario.hora_fin))

        hora_actual = hora_inicio_aware

        while hora_actual + duracion_visita <= hora_fin_aware:
            if hora_actual not in fechas_ocupadas:
                valor = hora_actual.isoformat()
                texto = hora_actual.strftime('%d de %B de %Y a las %H:%M %Z')
                huecos_disponibles.append((valor, texto))
            hora_actual += duracion_visita

    return huecos_disponibles


def agendar_visita_view(request, vivienda_id):
    """
    Formulario para que un arrendatario autorizado agende una visita.
    """
    vivienda = get_object_or_404(Vivienda, pk=vivienda_id)

    telefono_autorizado = request.session.get('telefono_autorizado')
    viviendas_autorizadas_ids = request.session.get('viviendas_autorizadas_ids', [])

    # --- Verificación de Seguridad Reforzada ---
    viviendas_autorizadas_ids = request.session.get('viviendas_autorizadas_ids', [])
    modificar_visita_id = request.session.get('modificar_visita_id')

    # El usuario debe tener la vivienda en su lista de autorizadas O estar modificando una visita.
    # Si está modificando, nos aseguramos de que la vivienda de la visita a modificar coincida con la URL.
    if vivienda_id not in viviendas_autorizadas_ids:
        if not modificar_visita_id or get_object_or_404(Visita, id=modificar_visita_id).vivienda.id != vivienda_id:
             return HttpResponseForbidden("No tienes permiso para solicitar una visita para esta vivienda.")

    visita_a_modificar = None
    modificar_visita_id = request.session.get('modificar_visita_id')
    if modificar_visita_id:
        visita_a_modificar = get_object_or_404(Visita, id=modificar_visita_id)

    horarios_disponibles = _get_horarios_disponibles(vivienda)

    if request.method == 'POST':
        form = AgendarVisitaForm(request.POST, instance=visita_a_modificar)
        form.fields['horario_disponible'].choices = horarios_disponibles

        if form.is_valid():
            # Si se está modificando, cancelamos la visita antigua primero.
            if visita_a_modificar:
                visita_a_modificar.estado = 'CANCELADA'
                visita_a_modificar.veces_cancelada += 1
                visita_a_modificar.save()
                # Limpiamos el ID de la sesión
                del request.session['modificar_visita_id']

            visita = form.save(commit=False)
            visita.vivienda = vivienda
            visita.telefono = visita_a_modificar.telefono if visita_a_modificar else telefono_autorizado
            visita.fecha_hora = datetime.fromisoformat(form.cleaned_data['horario_disponible'])
            visita.estado = 'CONFIRMADA' # Aseguramos que la nueva visita esté confirmada
            visita.save()

            # Enviar email de confirmación al arrendatario
            asunto = f"Confirmación de tu visita para {vivienda.nombre}"
            contexto_email = {
                'visita': visita,
                'vivienda': vivienda,
                'enlace_cancelacion': request.build_absolute_uri(reverse('propiedades:gestionar_visita', args=[visita.cancelacion_token]))
            }
            cuerpo_mensaje = render_to_string('propiedades/emails/confirmacion_visita.txt', contexto_email)
            html_cuerpo_mensaje = render_to_string('propiedades/emails/confirmacion_visita.html', contexto_email)

            try:
                msg = EmailMultiAlternatives(asunto, cuerpo_mensaje, settings.DEFAULT_FROM_EMAIL, [visita.email])
                msg.attach_alternative(html_cuerpo_mensaje, "text/html")
                msg.send()
                print(f"Correo de confirmación (modificación) enviado con éxito a {visita.email}.")
            except Exception as e:
                print(f"ERROR al enviar correo de confirmación (modificación): {e}")

            return redirect(reverse('propiedades:confirmacion_visita', args=[visita.cancelacion_token]))
    else:
        # Si estamos modificando, precargamos el formulario con los datos de la visita.
        form = AgendarVisitaForm(instance=visita_a_modificar)
        if not horarios_disponibles:
            form.fields['horario_disponible'].widget.attrs['disabled'] = True
            form.fields['horario_disponible'].help_text = "No hay horarios disponibles para esta vivienda en este momento."
        else:
            form.fields['horario_disponible'].choices = horarios_disponibles

    return render(request, 'propiedades/agendar_visita.html', {'form': form, 'vivienda': vivienda})


def confirmacion_visita_view(request, token):
    """
    Página que se muestra después de que el usuario agende una visita con éxito.
    """
    visita = get_object_or_404(Visita, cancelacion_token=token)
    return render(request, 'propiedades/confirmacion_visita.html', {'visita': visita})


def cancelar_visita_view(request, token):
    """
    Permite a un usuario cancelar una visita a través de un enlace único.
    """
    visita = get_object_or_404(Visita, cancelacion_token=token)

    if request.method == 'POST':
        mensaje = "Esta visita no se puede cancelar (ya estaba cancelada o realizada)."
        if visita.estado == 'CONFIRMADA':
            visita.estado = 'CANCELADA'
            visita.veces_cancelada += 1
            visita.save()

            # Enviar email de notificación a todos los administradores de la vivienda
            asunto = f"[Cancelación] Visita para {visita.vivienda.nombre} el {visita.fecha_hora.strftime('%d/%m')}"
            contexto_email = {'visita': visita}
            cuerpo_mensaje = render_to_string('propiedades/emails/notificacion_cancelacion_admin.txt', contexto_email)

            emails_admin = [admin.email for admin in visita.vivienda.administradores.all()]
            if emails_admin:
                html_cuerpo_mensaje = render_to_string('propiedades/emails/notificacion_cancelacion_admin.html', contexto_email)
                try:
                    msg = EmailMultiAlternatives(asunto, cuerpo_mensaje, settings.DEFAULT_FROM_EMAIL, emails_admin)
                    msg.attach_alternative(html_cuerpo_mensaje, "text/html")
                    msg.send()
                    print(f"Correo de cancelación enviado con éxito a los administradores: {', '.join(emails_admin)}.")
                except Exception as e:
                    print(f"ERROR al enviar correo de cancelación a admin: {e}")

            mensaje = "Tu visita ha sido cancelada con éxito."

        return render(request, 'propiedades/cancelar_visita.html', {'mensaje': mensaje})

    return render(request, 'propiedades/cancelar_visita.html', {'visita': visita})


def gestionar_visita_view(request, token):
    """
    Muestra los detalles de una visita existente y permite modificarla o cancelarla.
    """
    visita = get_object_or_404(Visita, cancelacion_token=token, estado='CONFIRMADA')

    if request.method == 'POST':
        if 'cancelar' in request.POST:
            # Si se hace clic en "Cancelar", redirigimos a la página de cancelación.
            return redirect(reverse('propiedades:cancelar_visita', args=[visita.cancelacion_token]))
        elif 'modificar' in request.POST:
            # Para "Modificar", guardamos los datos de la visita en la sesión para precargarlos.
            request.session['modificar_visita_id'] = visita.id
            request.session.save()

            # Redirigimos al formulario de agendar, que detectará la modificación.
            return redirect(reverse('propiedades:agendar_visita', args=[visita.vivienda.id]))

    return render(request, 'propiedades/gestionar_visita.html', {'visita': visita})


def seleccionar_vivienda_view(request):
    """
    Muestra una lista de viviendas autorizadas para que el usuario elija
    a cuál quiere solicitar una visita.
    """
    viviendas_ids = request.session.get('viviendas_autorizadas_ids', [])
    if not viviendas_ids:
        # Si no hay viviendas en la sesión, redirigimos al inicio del flujo.
        return redirect(reverse('propiedades:acceso_arrendatario'))

    viviendas = Vivienda.objects.filter(id__in=viviendas_ids)
    return render(request, 'propiedades/seleccionar_vivienda.html', {'viviendas': viviendas})


# Vista de ejemplo, mantener por ahora para que las URLs no fallen.
def solicitar_acceso_view(request, vivienda_id):
    return HttpResponse(f"Acceso solicitado para la vivienda {vivienda_id}.")