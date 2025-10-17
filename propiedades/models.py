import uuid
from django.db import models

class Administrador(models.Model):
    """
    Representa a un administrador de viviendas.
    """
    nombre = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

class Vivienda(models.Model):
    """
    Representa una vivienda para alquilar.
    """
    nombre = models.CharField(max_length=255)
    direccion_completa = models.TextField()
    referencia_catastral = models.CharField(max_length=20, unique=True)

    administradores = models.ManyToManyField(Administrador)

    nombre_aseguradora_impagos = models.CharField(max_length=200, blank=True)

    # Documentos
    contrato_modelo = models.FileField(upload_to='contratos/', blank=True, null=True)
    factura_luz = models.FileField(upload_to='facturas/luz/', blank=True, null=True)
    factura_agua = models.FileField(upload_to='facturas/agua/', blank=True, null=True)
    factura_gas = models.FileField(upload_to='facturas/gas/', blank=True, null=True)

    link_anuncio = models.URLField(max_length=500, blank=True)
    precio_mensualidad = models.DecimalField(max_digits=8, decimal_places=2)

    duracion_visita_minutos = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.nombre

class HorarioVisita(models.Model):
    """
    Define los horarios disponibles para visitar una vivienda en una fecha específica.
    """
    vivienda = models.ForeignKey(Vivienda, related_name='horarios', on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        # Evita que se creen múltiples franjas horarias idénticas para la misma vivienda en la misma fecha.
        unique_together = ('vivienda', 'fecha', 'hora_inicio', 'hora_fin')
        ordering = ['fecha', 'hora_inicio']

    def __str__(self):
        return f"{self.vivienda.nombre} - {self.fecha.strftime('%d/%m/%Y')} de {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')}"

class ArrendatarioAutorizado(models.Model):
    """
    Representa a un arrendatario cuyo teléfono ha sido autorizado por un administrador
    para solicitar una visita a una vivienda específica.
    """
    vivienda = models.ForeignKey(Vivienda, related_name='arrendatarios_autorizados', on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, help_text="Número de teléfono completo con prefijo internacional (ej. +34666666666)")

    class Meta:
        # Evita que el mismo número de teléfono se añada varias veces a la misma vivienda.
        unique_together = ('vivienda', 'telefono')
        verbose_name = "Arrendatario Autorizado"
        verbose_name_plural = "Arrendatarios Autorizados"

    def __str__(self):
        return f"{self.telefono} autorizado para {self.vivienda.nombre}"

class Visita(models.Model):
    """
    Almacena la información de una solicitud de visita de un arrendatario.
    """
    ESTADO_CHOICES = [
        ("CONFIRMADA", "Confirmada"),
        ("CANCELADA", "Cancelada"),
        ("REALIZADA", "Realizada"),
    ]

    # Relaciones
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE, related_name="visitas")

    # Datos del solicitante
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)

    # Información para el seguro
    sueldo_mensual = models.DecimalField(max_digits=10, decimal_places=2, help_text="Sueldo mensual bruto en euros")
    numero_inquilinos = models.PositiveIntegerField(default=1)
    numero_menores = models.PositiveIntegerField(default=0)
    mascota = models.BooleanField(default=False, help_text="¿Tiene mascotas?")
    puesto_trabajo = models.TextField(help_text="Describa los puestos de trabajo de los inquilinos adultos")
    fumador = models.BooleanField(default=False, help_text="¿Es fumador?")
    observaciones = models.TextField(blank=True, null=True)

    # Datos de la cita
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="CONFIRMADA")

    # Metadatos
    cancelacion_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    veces_cancelada = models.PositiveIntegerField(default=0)
    motivo_cancelacion = models.CharField(max_length=255, blank=True, null=True, help_text="Motivo por el que se canceló la visita.")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        # Evita que se agende más de una visita para la misma vivienda a la misma hora.
        unique_together = ('vivienda', 'fecha_hora')
        ordering = ['fecha_hora']
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"

    def __str__(self):
        return f"Visita de {self.nombre} {self.apellidos} para {self.vivienda.nombre} el {self.fecha_hora.strftime('%d/%m/%Y a las %H:%M')}"


class SolicitudDeDocumentacion(models.Model):
    """
    Representa una solicitud de documentación a un candidato seleccionado.
    """
    ESTADO_SOLICITUD = [
        ('PENDIENTE', 'Pendiente de envío de documentos'),
        ('COMPLETADA', 'Documentación recibida'),
        ('EN_REVISION', 'En revisión'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    visita = models.OneToOneField(Visita, on_delete=models.CASCADE, related_name="solicitud_de_documentacion")
    estado = models.CharField(max_length=20, choices=ESTADO_SOLICITUD, default='PENDIENTE')
    token_acceso = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solicitud de documentación para {self.visita.nombre} {self.visita.apellidos}"


class InquilinoDocumentacion(models.Model):
    """
    Almacena los datos y documentos de una persona (inquilino) asociados a una
    solicitud de documentación.
    """
    solicitud = models.ForeignKey(SolicitudDeDocumentacion, on_delete=models.CASCADE, related_name="inquilino_documentacion")

    # Datos del inquilino
    nombre_completo = models.CharField(max_length=255)
    dni_nif_nie = models.CharField(max_length=20)

    # Documentos
    dni_anverso = models.FileField(upload_to='documentacion/dni_anverso/')
    dni_reverso = models.FileField(upload_to='documentacion/dni_reverso/')
    contrato_trabajo = models.FileField(upload_to='documentacion/contrato_trabajo/', blank=True, null=True)
    ultima_nomina = models.FileField(upload_to='documentacion/nominas/', blank=True, null=True)
    penultima_nomina = models.FileField(upload_to='documentacion/nominas/', blank=True, null=True)
    antepenultima_nomina = models.FileField(upload_to='documentacion/nominas/', blank=True, null=True)
    renta_anual = models.FileField(upload_to='documentacion/renta/', blank=True, null=True, help_text="Para autónomos")
    iban = models.CharField(max_length=34)

    def __str__(self):
        return f"Documentación de {self.nombre_completo} para solicitud {self.solicitud.id}"
