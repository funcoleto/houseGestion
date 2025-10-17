from django.db import models

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
