from django.urls import path
from . import views

app_name = 'propiedades'

urlpatterns = [
    path('acceso-arrendatario/', views.acceso_arrendatario_view, name='acceso_arrendatario'),
    path('vivienda/<int:vivienda_id>/agendar-visita/', views.agendar_visita_view, name='agendar_visita'),
    path('visita/confirmacion/<uuid:token>/', views.confirmacion_visita_view, name='confirmacion_visita'),
    path('visita/cancelar/<uuid:token>/', views.cancelar_visita_view, name='cancelar_visita'),
    path('visita/gestionar/<uuid:token>/', views.gestionar_visita_view, name='gestionar_visita'),
    path('seleccionar-vivienda/', views.seleccionar_vivienda_view, name='seleccionar_vivienda'),
    path('solicitud-documentacion/<uuid:token>/', views.subir_documentos_view, name='subir_documentos'),
]