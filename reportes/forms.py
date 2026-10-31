from django import forms

from core.forms import FormularioBase
from reportes.models import Comentario, ReporteAmbiental


class ReporteForm(FormularioBase):
    """Registro y edición de un reporte ambiental (RF-10)."""

    class Meta:
        model = ReporteAmbiental
        fields = [
            'titulo', 'descripcion', 'gravedad', 'municipio', 'direccion',
            'latitud', 'longitud', 'fotografia',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fotografia': forms.ClearableFileInput(attrs={'accept': '.jpg,.jpeg,.png'}),
        }
        help_texts = {
            'latitud': 'Entre 13.0 y 14.5. Ejemplo: 14.035000',
            'longitud': 'Entre -90.2 y -87.6. Ejemplo: -88.945000',
            'fotografia': 'Opcional. Formato JPG o PNG, máximo 5 MB.',
            'direccion': 'Opcional: una referencia para ubicar el lugar.',
        }


class ComentarioForm(FormularioBase):
    """Comentario sobre un reporte (RF-21)."""

    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Escriba un comentario...'}),
        }
        labels = {'texto': ''}