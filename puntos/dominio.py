from core.base import EntidadBase, Ubicable


class Material(EntidadBase):
    """Tipo de material reciclable y cómo prepararlo para entregarlo."""

    CATEGORIAS = (
        'Plástico', 'Papel y cartón', 'Metal', 'Vidrio',
        'Electrónico', 'Orgánico', 'Otro',
    )

    def __init__(self, nombre, categoria, indicaciones=''):
        super().__init__()
        self.nombre = nombre
        self.categoria = categoria
        self.indicaciones = indicaciones

    def validar(self):
        if not self.nombre.strip():
            raise ValueError('El material debe tener un nombre.')
        if self.categoria not in self.CATEGORIAS:
            raise ValueError(f'Categoría no válida: {self.categoria}.')

    def __str__(self):
        return self.nombre


class PuntoRecepcion(Ubicable):
    """Lugar donde se entregan materiales reciclables."""

    CONFIRMADA = 'CONFIRMADA'
    POR_CONFIRMAR = 'POR_CONFIRMAR'

    def __init__(self, nombre, tipo, direccion, latitud, longitud, municipio,
                 horario='', gestor=None):
        super().__init__(direccion, latitud, longitud, municipio)
        self.nombre = nombre
        self.tipo = tipo
        self.horario = horario
        self.gestor = gestor
        self.estado_informacion = self.POR_CONFIRMAR
        self.activo = True
        self._materiales = {}  # nombre del material -> (material, observaciones)

    # --- Materiales que recibe (relación PuntoMaterial) ---

    def agregar_material(self, material, observaciones=''):
        """Agrega un material; no puede repetirse en el mismo punto."""
        if material.nombre in self._materiales:
            raise ValueError(f'{self.nombre} ya recibe {material.nombre}.')
        self._materiales[material.nombre] = (material, observaciones)

    def quitar_material(self, material):
        self._materiales.pop(material.nombre, None)

    def recibe(self, nombre_material):
        return nombre_material in self._materiales

    @property
    def materiales(self):
        return [material for material, _ in self._materiales.values()]

    # --- Estado de la información (RF-19) ---

    def confirmar_informacion(self):
        self.estado_informacion = self.CONFIRMADA

    # --- Métodos heredados ---

    def validar(self):
        super().validar()
        if not self.nombre.strip():
            raise ValueError('El punto debe tener un nombre.')

    def obtener_marcador(self):
        return {
            'tipo': 'punto',
            'titulo': self.nombre,
            'icono': 'reciclaje',
            'latitud': self.latitud,
            'longitud': self.longitud,
        }

    def mostrar_detalle(self):
        materiales = ', '.join(m.nombre for m in self.materiales) or 'Sin materiales registrados'
        return (
            f'{self.nombre} ({self.tipo}) · {self.municipio}. '
            f'Recibe: {materiales}. Información: {self.estado_informacion}.'
        )

    def __str__(self):
        return self.nombre


def filtrar_puntos(puntos, municipio=None, material=None):
    """Filtra puntos activos por municipio y por material (RF-05)."""
    resultado = [punto for punto in puntos if punto.activo]
    if municipio:
        resultado = [p for p in resultado if p.municipio == municipio]
    if material:
        resultado = [p for p in resultado if p.recibe(material)]
    return resultado