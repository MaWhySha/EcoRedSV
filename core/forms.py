from django import forms


class FormularioBase(forms.ModelForm):
    """
    Formulario base del proyecto: aplica automáticamente las clases de Bootstrap
    a cada campo según su tipo. Los formularios de las apps heredan de esta clase.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'form-check-input'
            elif isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs['class'] = 'form-check-input'
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs['class'] = 'form-select'
            else:
                widget.attrs['class'] = 'form-control'

            # Texto en español para la opción vacía de las listas
            if isinstance(campo, forms.ModelChoiceField) and campo.empty_label is not None:
                campo.empty_label = 'Seleccione una opción'


class CampoFechaHora(forms.DateTimeInput):
    """Selector de fecha y hora del navegador."""

    input_type = 'datetime-local'

    def __init__(self, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%dT%H:%M')
        super().__init__(**kwargs)