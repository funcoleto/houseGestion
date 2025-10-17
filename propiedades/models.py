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
    Define los horarios disponibles para visitar una vivienda.
    """
    DIAS_SEMANA = [
        ("lunes", "Lunes"),
        ("martes", "Martes"),
        ("miercoles", "Miércoles"),
        ("jueves", "Jueves"),
        ("viernes", "Viernes"),
        ("sabado", "Sábado"),
        ("domingo", "Domingo"),
    ]

    vivienda = models.ForeignKey(Vivienda, related_name='horarios', on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        unique_together = ('vivienda', 'dia_semana', 'hora_inicio', 'hora_fin')

    def __str__(self):
        return f"{self.vivienda.nombre} - {self.get_dia_semana_display()} de {self.hora_inicio} a {self.hora_fin}"
