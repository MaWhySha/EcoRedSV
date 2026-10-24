from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class EntidadBase(models.Model):
    """
    Base abstracta de todos los modelos del sistema.
    No genera tabla: aporta la validación común antes de guardar.
    """

    class Meta:
        abstract = True

    def validar(self):
        """Ejecuta todas las validaciones del modelo, incluidas las de clean()."""
        self.full_clean()

    def guardar(self):
        """Valida el objeto con sus reglas y lo guarda en la base de datos."""
        self.validar()
        self.save()
        return self


class Ubicable(EntidadBase):
    """
    Base abstracta de los elementos que se muestran en el mapa:
    puntos de recepción, campañas y reportes ambientales.
    """

    # Límites aproximados de El Salvador
    LATITUD_MIN, LATITUD_MAX = Decimal('13.0'), Decimal('14.5')
    LONGITUD_MIN, LONGITUD_MAX = Decimal('-90.2'), Decimal('-87.6')

    direccion = models.CharField('dirección', max_length=250)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    municipio = models.ForeignKey(
        'usuarios.Municipio',
        on_delete=models.PROTECT,
        db_column='id_municipio',
    )

    class Meta:
        abstract = True

    def clean(self):
        """Comprueba que las coordenadas estén dentro de El Salvador."""
        super().clean()
        if self.latitud is not None and not (self.LATITUD_MIN <= self.latitud <= self.LATITUD_MAX):
            raise ValidationError({'latitud': 'La latitud está fuera de El Salvador.'})
        if self.longitud is not None and not (self.LONGITUD_MIN <= self.longitud <= self.LONGITUD_MAX):
            raise ValidationError({'longitud': 'La longitud está fuera de El Salvador.'})

    # Métodos abstractos: cada subclase los define a su manera (polimorfismo).
    # Se usa NotImplementedError porque los modelos de Django no admiten ABC.
    def obtener_marcador(self):
        raise NotImplementedError('Cada subclase define su marcador.')

    def mostrar_detalle(self):
        raise NotImplementedError('Cada subclase define su detalle.')