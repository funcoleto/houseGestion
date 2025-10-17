from django import forms
from django.forms import modelformset_factory
from .models import Visita, ArrendatarioAutorizado, DocumentoInquilino
import re

class AccesoArrendatarioForm(forms.Form):
    """
    Formulario para que el arrendatario introduzca su número de teléfono.
    """
    telefono = forms.CharField(
        label="Tu número de teléfono (con prefijo internacional)",
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': '+34666666666'})
    )

    def clean_telefono(self):
        """
        Limpia y normaliza el número de teléfono para asegurar un formato consistente.
        Elimina espacios y guiones.
        """
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Elimina todo lo que no sea un dígito o el signo '+' inicial.
            telefono_limpio = re.sub(r'[^\d+]', '', telefono)
            if not telefono_limpio.startswith('+'):
                raise forms.ValidationError("El número de teléfono debe incluir el prefijo internacional (ej. +34).")
            return telefono_limpio
        return telefono

class AgendarVisitaForm(forms.ModelForm):
    """
    Formulario para que el arrendatario rellene sus datos y elija una hora de visita.
    """
    # Este campo se rellenará dinámicamente desde la vista con los horarios disponibles.
    horario_disponible = forms.ChoiceField(
        label="Selecciona un horario de visita",
        choices=[], # Se rellena en la vista
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Visita
        # Campos que el usuario debe rellenar.
        fields = [
            'nombre', 'apellidos', 'email',
            'sueldo_mensual', 'numero_inquilinos', 'numero_menores',
            'mascota', 'fumador', 'puesto_trabajo', 'observaciones',
            'horario_disponible'
        ]
        widgets = {
            'puesto_trabajo': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

class DocumentoInquilinoForm(forms.ModelForm):
    """
    Formulario para que un inquilino suba sus datos y documentos.
    """
    class Meta:
        model = DocumentoInquilino
        fields = [
            'nombre_completo', 'dni_nif_nie', 'iban',
            'dni_anverso', 'dni_reverso',
            'contrato_trabajo', 'ultima_nomina', 'penultima_nomina', 'antepenultima_nomina',
            'renta_anual'
        ]
        labels = {
            'nombre_completo': 'Nombre completo',
            'dni_nif_nie': 'DNI / NIF / NIE',
            'iban': 'Cuenta IBAN',
            'dni_anverso': 'DNI / NIE (Cara anverso)',
            'dni_reverso': 'DNI / NIE (Cara reverso)',
            'contrato_trabajo': 'Contrato de trabajo',
            'ultima_nomina': 'Última nómina',
            'penultima_nomina': 'Penúltima nómina',
            'antepenultima_nomina': 'Antepenúltima nómina',
            'renta_anual': 'Última declaración de la renta (solo autónomos)',
        }

# Usamos un formset para permitir la subida de documentos para múltiples inquilinos.
# 'extra=4' significa que por defecto se mostrarán 4 formularios vacíos.
DocumentoInquilinoFormSet = modelformset_factory(
    DocumentoInquilino,
    form=DocumentoInquilinoForm,
    extra=4,
    can_delete=True # Permite eliminar formularios añadidos
)