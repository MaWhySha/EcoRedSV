from abc import ABC, abstractmethod

from django.utils import timezone


class EntidadBase(ABC):
    """Base de todas las clases del sistema: fechas y validación común."""

    def __init__(self):
        self._creado_en = timezone.now()
        self._actualizado_en = self._creado_en

    @property
    def creado_en(self):
        return self._creado_en

    @property
    def actualizado_en(self):
        return self._actualizado_en

    @abstractmethod
    def validar(self):
        """Cada subclase define sus reglas. Lanza ValueError si algo no es válido."""

    def guardar(self):
        """Valida el objeto y actualiza la fecha de modificación."""
        self.validar()
        self._actualizado_en = timezone.now()
        return True


class Ubicable(EntidadBase):
    """Elemento con ubicación que puede mostrarse en el mapa."""

    # Límites aproximados de El Salvador
    LATITUD_MIN, LATITUD_MAX = 13.0, 14.5
    LONGITUD_MIN, LONGITUD_MAX = -90.2, -87.6

    def __init__(self, direccion, latitud, longitud, municipio):
        super().__init__()
        self.direccion = direccion
        self.latitud = latitud
        self.longitud = longitud
        self.municipio = municipio

    def validar(self):
        """Comprueba que las coordenadas estén dentro de El Salvador."""
        if not (self.LATITUD_MIN <= self.latitud <= self.LATITUD_MAX):
            raise ValueError('La latitud está fuera de El Salvador.')
        if not (self.LONGITUD_MIN <= self.longitud <= self.LONGITUD_MAX):
            raise ValueError('La longitud está fuera de El Salvador.')

    @abstractmethod
    def obtener_marcador(self):
        """Devuelve los datos del marcador que se dibuja en el mapa."""

    @abstractmethod
    def mostrar_detalle(self):
        """Devuelve la información que se muestra al seleccionar el elemento."""


def construir_marcadores(elementos):
    """
    Genera los marcadores del mapa sin importar el tipo de cada elemento.
    Cada clase responde a obtener_marcador() a su manera (polimorfismo).
    """
    return [elemento.obtener_marcador() for elemento in elementos]