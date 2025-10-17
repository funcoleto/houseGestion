from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseForbidden
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
                    # TODO: Implementar una página de selección si hay múltiples viviendas.
                    return redirect(reverse('propiedades:agendar_visita', args=[viviendas_ids[0]]))
    else:
        form = AccesoArrendatarioForm()

    return render(request, 'propiedades/acceso_arrendatario.html', {'form': form})


def _get_horarios_disponibles(vivienda):
    """
    Calcula y devuelve una lista de tuplas con los huecos de visita disponibles.
    """
    duracion_visita = timedelta(minutes=vivienda.duracion_visita_minutos)
    # Solo consideramos horarios futuros.
    horarios_definidos = HorarioVisita.objects.filter(vivienda=vivienda, fecha__gte=datetime.today().date()).order_by('fecha', 'hora_inicio')
    visitas_confirmadas = Visita.objects.filter(vivienda=vivienda, estado='CONFIRMADA', fecha_hora__gte=datetime.now())

    fechas_ocupadas = {v.fecha_hora for v in visitas_confirmadas}
    huecos_disponibles = []

    for horario in horarios_definidos:
        hora_actual = datetime.combine(horario.fecha, horario.hora_inicio)
        hora_fin_franja = datetime.combine(horario.fecha, horario.hora_fin)

        while hora_actual + duracion_visita <= hora_fin_franja:
            if hora_actual not in fechas_ocupadas:
                valor = hora_actual.isoformat()
                texto = hora_actual.strftime('%d de %B de %Y a las %H:%M')
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

    if not telefono_autorizado or vivienda_id not in viviendas_autorizadas_ids:
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    horarios_disponibles = _get_horarios_disponibles(vivienda)

    if request.method == 'POST':
        form = AgendarVisitaForm(request.POST)
        form.fields['horario_disponible'].choices = horarios_disponibles

        if form.is_valid():
            visita = form.save(commit=False)
            visita.vivienda = vivienda
            visita.telefono = telefono_autorizado
            visita.fecha_hora = datetime.fromisoformat(form.cleaned_data['horario_disponible'])
            visita.save()

            # Simulación de envío de email
            print(f"--- EMAIL DE CONFIRMACIÓN (simulado) ---")
            print(f"Para: {visita.email}")
            print(f"Asunto: Confirmación de tu visita para {vivienda.nombre}")
            print(f"Cuerpo: Hola {visita.nombre}, tu visita está confirmada para el {visita.fecha_hora.strftime('%d/%m/%Y a las %H:%M')}.")
            print(f"Para cancelar, visita: {request.build_absolute_uri(reverse('propiedades:cancelar_visita', args=[visita.cancelacion_token]))}")
            print(f"--------------------------------------")

            return redirect(reverse('propiedades:confirmacion_visita', args=[visita.cancelacion_token]))
    else:
        form = AgendarVisitaForm()
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

            # Simulación de email de notificación al administrador
            print(f"--- EMAIL DE NOTIFICACIÓN A ADMIN (simulado) ---")
            print(f"Asunto: Visita cancelada para {visita.vivienda.nombre}")
            print(f"Cuerpo: La visita de {visita.nombre} para el {visita.fecha_hora.strftime('%d/%m/%Y')} ha sido cancelada por el usuario.")
            print(f"---------------------------------------------")

            mensaje = "Tu visita ha sido cancelada con éxito."

        return render(request, 'propiedades/cancelar_visita.html', {'mensaje': mensaje})

    return render(request, 'propiedades/cancelar_visita.html', {'visita': visita})


# Vista de ejemplo, mantener por ahora para que las URLs no fallen.
def solicitar_acceso_view(request, vivienda_id):
    return HttpResponse(f"Acceso solicitado para la vivienda {vivienda_id}.")