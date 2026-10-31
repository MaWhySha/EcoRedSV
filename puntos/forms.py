from django import forms

from core.forms import FormularioBase
from puntos.models import Material, PuntoMaterial, PuntoRecepcion
from usuarios.models import Usuario


class PuntoRecepcionForm(FormularioBase):
    """Registro y edición de un punto de recepción (RF-06, RF-07)."""

    class Meta:
        model = PuntoRecepcion
        fields = [
            'nombre', 'tipo', 'municipio', 'direccion', 'latitud', 'longitud',
            'horario', 'condiciones_entrega', 'telefono_contacto', 'gestor', 'activo',
        ]
        widgets = {
            'condiciones_entrega': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'latitud': 'Entre 13.0 y 14.5. Ejemplo: 14.040000',
            'longitud': 'Entre -90.2 y -87.6. Ejemplo: -88.938000',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo se puede asignar como gestor a usuarios con ese rol
        self.fields['gestor'].queryset = Usuario.objects.filter(rol=Usuario.Rol.GESTOR, is_active=True)


class MaterialForm(FormularioBase):
    """Registro y edición del catálogo de materiales."""

    class Meta:
        model = Material
        fields = ['nombre', 'categoria', 'descripcion', 'indicaciones']
        widgets = {
            'indicaciones': forms.Textarea(attrs={'rows': 3}),
        }


class AgregarMaterialForm(FormularioBase):
    """Agrega un material a un punto, con su condición particular."""

    class Meta:
        model = PuntoMaterial
        fields = ['material', 'observaciones']

    def __init__(self, *args, punto=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo se ofrecen los materiales que el punto todavía no recibe
        if punto is not None:
            self.fields['material'].queryset = Material.objects.exclude(puntos=punto)
        self.fields['observaciones'].widget.attrs['placeholder'] = 'Opcional: por ejemplo, solo botellas sin tapón'