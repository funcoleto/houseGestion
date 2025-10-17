from django.urls import path
from . import views

app_name = 'propiedades'

urlpatterns = [
    # Ejemplo: /viviendas/1/solicitar-acceso/
    path('viviendas/<int:vivienda_id>/solicitar-acceso/', views.solicitar_acceso_view, name='solicitar_acceso'),

    # Ejemplo: /solicitar-visita/ (Página para introducir el teléfono)
    # Por ahora, vamos a crear una URL genérica para el acceso.
    # La lógica de a qué vivienda pertenece el teléfono se hará en la vista.
    path('acceso-arrendatario/', views.acceso_arrendatario_view, name='acceso_arrendatario'),

    # Ejemplo: /vivienda/1/agendar-visita/
    path('vivienda/<int:vivienda_id>/agendar-visita/', views.agendar_visita_view, name='agendar_visita'),

    # Ejemplo: /visita/confirmacion/a1b2c3d4.../
    path('visita/confirmacion/<uuid:token>/', views.confirmacion_visita_view, name='confirmacion_visita'),

    # Ejemplo: /visita/cancelar/a1b2c3d4.../
    path('visita/cancelar/<uuid:token>/', views.cancelar_visita_view, name='cancelar_visita'),
]