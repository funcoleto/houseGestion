from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

from .forms import AccesoArrendatarioForm, AgendarVisitaForm, DocumentacionInquilinoFormSet
from .models import ArrendatarioAutorizado, Vivienda, Visita, HorarioVisita, SolicitudDocumentacion, DocumentacionInquilino

# --- Vistas del Flujo del Arrendatario (Proceso 1) ---

def acceso_arrendatario_view(request):
    if request.method == 'POST':
        form = AccesoArrendatarioForm(request.POST)
        if form.is_valid():
            telefono = form.cleaned_data['telefono']
            autorizaciones = ArrendatarioAutorizado.objects.filter(telefono=telefono)
            viviendas_ids = list(autorizaciones.values_list('vivienda_id', flat=True))
            if not viviendas_ids:
                form.add_error('telefono', 'Este número de teléfono no está autorizado para visitar ninguna vivienda.')
            else:
                request.session['telefono_autorizado'] = telefono
                request.session['viviendas_autorizadas_ids'] = viviendas_ids
                request.session.save()
                return redirect(reverse('propiedades:seleccionar_vivienda'))
    else:
        form = AccesoArrendatarioForm()
    return render(request, 'propiedades/acceso_arrendatario.html', {'form': form})

def seleccionar_vivienda_view(request):
    telefono = request.session.get('telefono_autorizado')
    viviendas_ids = request.session.get('viviendas_autorizadas_ids', [])
    if not telefono or not viviendas_ids:
        return redirect(reverse('propiedades:acceso_arrendatario'))
    viviendas_autorizadas = Vivienda.objects.filter(id__in=viviendas_ids)
    visitas_activas = Visita.objects.filter(telefono=telefono, vivienda_id__in=viviendas_ids, estado='CONFIRMADA').values('vivienda_id', 'cancelacion_token')
    mapa_visitas = {item['vivienda_id']: item['cancelacion_token'] for item in visitas_activas}
    viviendas_con_estado = []
    for vivienda in viviendas_autorizadas:
        token = mapa_visitas.get(vivienda.id)
        viviendas_con_estado.append({'vivienda': vivienda, 'visita_token': token})
    return render(request, 'propiedades/seleccionar_vivienda.html', {'viviendas_con_estado': viviendas_con_estado})

def agendar_visita_view(request, vivienda_id):
    vivienda = get_object_or_404(Vivienda, pk=vivienda_id)
    viviendas_autorizadas_ids = request.session.get('viviendas_autorizadas_ids', [])
    modificar_visita_id = request.session.get('modificar_visita_id')
    if vivienda_id not in viviendas_autorizadas_ids:
        if not modificar_visita_id or get_object_or_404(Visita, id=modificar_visita_id).vivienda.id != vivienda_id:
             return HttpResponseForbidden("No tienes permiso para solicitar una visita para esta vivienda.")
    visita_a_modificar = None
    if modificar_visita_id:
        visita_a_modificar = get_object_or_404(Visita, id=modificar_visita_id)
    horarios_disponibles = _get_horarios_disponibles(vivienda)
    if request.method == 'POST':
        form = AgendarVisitaForm(request.POST, instance=visita_a_modificar)
        form.fields['horario_disponible'].choices = horarios_disponibles
        if form.is_valid():
            if visita_a_modificar:
                visita_a_modificar.estado = 'CANCELADA'
                visita_a_modificar.veces_cancelada += 1
                visita_a_modificar.save()
                del request.session['modificar_visita_id']
            visita = form.save(commit=False)
            visita.vivienda = vivienda
            visita.telefono = visita_a_modificar.telefono if visita_a_modificar else request.session.get('telefono_autorizado')
            visita.fecha_hora = datetime.fromisoformat(form.cleaned_data['horario_disponible'])
            visita.estado = 'CONFIRMADA'
            visita.save()
            asunto = f"Confirmación de tu visita para {vivienda.nombre}"
            contexto_email = {'visita': visita, 'vivienda': vivienda, 'enlace_cancelacion': request.build_absolute_uri(reverse('propiedades:gestionar_visita', args=[visita.cancelacion_token]))}
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
        form = AgendarVisitaForm(instance=visita_a_modificar)
        if not horarios_disponibles:
            form.fields['horario_disponible'].widget.attrs['disabled'] = True
            form.fields['horario_disponible'].help_text = "No hay horarios disponibles para esta vivienda en este momento."
        else:
            form.fields['horario_disponible'].choices = horarios_disponibles
    return render(request, 'propiedades/agendar_visita.html', {'form': form, 'vivienda': vivienda})

def _get_horarios_disponibles(vivienda):
    duracion_visita = timedelta(minutes=vivienda.duracion_visita_minutos)
    horarios_definidos = HorarioVisita.objects.filter(vivienda=vivienda, fecha__gte=timezone.now().date()).order_by('fecha', 'hora_inicio')
    visitas_confirmadas = Visita.objects.filter(vivienda=vivienda, estado='CONFIRMADA', fecha_hora__gte=timezone.now())
    fechas_ocupadas = {v.fecha_hora for v in visitas_confirmadas}
    huecos_disponibles = []
    for horario in horarios_definidos:
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

def confirmacion_visita_view(request, token):
    visita = get_object_or_404(Visita, cancelacion_token=token)
    return render(request, 'propiedades/confirmacion_visita.html', {'visita': visita})

def cancelar_visita_view(request, token):
    visita = get_object_or_404(Visita, cancelacion_token=token)
    if request.method == 'POST':
        mensaje = "Esta visita no se puede cancelar (ya estaba cancelada o realizada)."
        if visita.estado == 'CONFIRMADA':
            visita.estado = 'CANCELADA'
            visita.veces_cancelada += 1
            visita.save()
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
    visita = get_object_or_404(Visita, cancelacion_token=token, estado='CONFIRMADA')
    if request.method == 'POST':
        if 'cancelar' in request.POST:
            return redirect(reverse('propiedades:cancelar_visita', args=[visita.cancelacion_token]))
        elif 'modificar' in request.POST:
            request.session['modificar_visita_id'] = visita.id
            request.session.save()
            return redirect(reverse('propiedades:agendar_visita', args=[visita.vivienda.id]))
    return render(request, 'propiedades/gestionar_visita.html', {'visita': visita})

# --- Vistas del Flujo del Proceso 2 ---

def subir_documentos_view(request, token):
    solicitud = get_object_or_404(SolicitudDocumentacion, token_acceso=token)
    if solicitud.estado != 'PENDIENTE':
        return render(request, 'propiedades/subida_documentos_completada.html', {'solicitud': solicitud})
    if request.method == 'POST':
        formset = DocumentacionInquilinoFormSet(request.POST, request.FILES, queryset=solicitud.documentacion_inquilinos.none())
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.solicitud = solicitud
                instance.save()
            solicitud.estado = 'COMPLETADA'
            solicitud.save()
            return render(request, 'propiedades/subida_documentos_completada.html', {'solicitud': solicitud})
    else:
        formset = DocumentacionInquilinoFormSet(queryset=solicitud.documentacion_inquilinos.none())
    return render(request, 'propiedades/subir_documentos.html', {'solicitud': solicitud, 'formset': formset})