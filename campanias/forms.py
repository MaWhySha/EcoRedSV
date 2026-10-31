from django import forms

from campanias.models import Campania, RegistroRecoleccion
from core.forms import CampoFechaHora, FormularioBase


class CampaniaForm(FormularioBase):
    """Registro y edición de campañas (RF-08)."""

    class Meta:
        model = Campania
        fields = [
            'titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'municipio', 'direccion',
            'latitud', 'longitud', 'organizacion', 'punto', 'materiales',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_inicio': CampoFechaHora(),
            'fecha_fin': CampoFechaHora(),
            'materiales': forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            'latitud': 'Entre 13.0 y 14.5. Ejemplo: 14.032000',
            'longitud': 'Entre -90.2 y -87.6. Ejemplo: -88.942000',
            'punto': 'Opcional: punto de recepción donde se realiza la jornada.',
            'organizacion': 'Opcional: organización responsable.',
        }


class RegistroPesoForm(FormularioBase):
    """Registro de los kilogramos recolectados de un material (RF-17)."""

    class Meta:
        model = RegistroRecoleccion
        fields = ['material', 'peso_kg', 'observaciones']

    def __init__(self, *args, campania=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo los materiales que recibe la campaña
        if campania is not None:
            self.fields['material'].queryset = campania.materiales.all()
        self.fields['peso_kg'].widget.attrs.update({'min': '0.01', 'step': '0.01', 'placeholder': 'Kg'})
        self.fields['observaciones'].widget.attrs['placeholder'] = 'Opcional'