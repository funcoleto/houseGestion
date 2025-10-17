from django import forms
from .models import Visita, ArrendatarioAutorizado
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