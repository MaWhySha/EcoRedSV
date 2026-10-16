from decimal import Decimal

from django.utils import timezone

from core.base import EntidadBase, Ubicable
from usuarios.permisos import Accion


class Participacion(EntidadBase):
    """Inscripción de un usuario a una campaña (RF-16)."""

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.fecha_inscripcion = timezone.now()
        self.asistio = False

    def confirmar_asistencia(self):
        self.asistio = True

    def validar(self):
        if self.usuario is None:
            raise ValueError('La participación necesita un usuario.')


class RegistroRecoleccion(EntidadBase):
    """Kilogramos recolectados de un material en una campaña (RF-17)."""

    def __init__(self, material, peso_kg, registrado_por):
        super().__init__()
        self.material = material
        self.registrado_por = registrado_por
        self.peso_kg = peso_kg  # pasa por el setter, que valida

    @property
    def peso_kg(self):
        return self._peso_kg

    @peso_kg.setter
    def peso_kg(self, valor):
        valor = Decimal(str(valor))
        if valor <= 0:
            raise ValueError('El peso debe ser mayor que cero.')
        self._peso_kg = valor

    def validar(self):
        if self._peso_kg <= 0:
            raise ValueError('El peso debe ser mayor que cero.')


class Campania(Ubicable):
    """Campaña o jornada de recolección."""

    PROGRAMADA = 'PROGRAMADA'
    EN_CURSO = 'EN_CURSO'
    FINALIZADA = 'FINALIZADA'
    CANCELADA = 'CANCELADA'

    # Cambios de estado permitidos
    TRANSICIONES = {
        PROGRAMADA: {EN_CURSO, CANCELADA},
        EN_CURSO: {FINALIZADA, CANCELADA},
        FINALIZADA: set(),
        CANCELADA: set(),
    }

    def __init__(self, titulo, fecha_inicio, fecha_fin, direccion, latitud,
                 longitud, municipio, creador, organizacion=None, punto=None):
        super().__init__(direccion, latitud, longitud, municipio)
        self.titulo = titulo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.creador = creador
        self.organizacion = organizacion  # opcional
        self.punto = punto                # opcional
        self._estado = self.PROGRAMADA
        self.materiales = []
        self._participaciones = {}  # nombre de usuario -> Participacion
        self._registros = []

    @property
    def estado(self):
        return self._estado

    def cambiar_estado(self, nuevo):
        """Cambia el estado solo si la transición está permitida."""
        if nuevo not in self.TRANSICIONES[self._estado]:
            raise ValueError(f'No se puede pasar de {self._estado} a {nuevo}.')
        self._estado = nuevo

    def inscribir(self, perfil):
        """Inscribe a un usuario una sola vez (RF-16)."""
        if not perfil.tiene_permiso(Accion.INSCRIBIRSE):
            raise PermissionError('El usuario no puede inscribirse (¿correo verificado?).')
        if self._estado in (self.FINALIZADA, self.CANCELADA):
            raise ValueError('La campaña ya no admite inscripciones.')
        if perfil.nombre_usuario in self._participaciones:
            raise ValueError('El usuario ya está inscrito.')
        participacion = Participacion(perfil.nombre_usuario)
        self._participaciones[perfil.nombre_usuario] = participacion
        return participacion

    @property
    def total_inscritos(self):
        return len(self._participaciones)

    def registrar_peso(self, material, peso_kg, perfil):
        """Registra kilogramos recolectados (RF-17)."""
        if not perfil.tiene_permiso(Accion.REGISTRAR_PESO):
            raise PermissionError('El usuario no puede registrar pesos.')
        if self._estado not in (self.EN_CURSO, self.FINALIZADA):
            raise ValueError('Solo se registra peso en campañas en curso o finalizadas.')
        if material not in self.materiales:
            raise ValueError(f'La campaña no recibe {material.nombre}.')
        registro = RegistroRecoleccion(material, peso_kg, perfil.nombre_usuario)
        self._registros.append(registro)
        return registro

    def total_recolectado(self):
        """Total de kilogramos por material (RF-18)."""
        totales = {}
        for registro in self._registros:
            nombre = registro.material.nombre
            totales[nombre] = totales.get(nombre, Decimal('0')) + registro.peso_kg
        return totales

    def validar(self):
        super().validar()
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError('La fecha de fin no puede ser anterior al inicio.')

    def obtener_marcador(self):
        return {
            'tipo': 'campania',
            'titulo': self.titulo,
            'icono': 'calendario',
            'latitud': self.latitud,
            'longitud': self.longitud,
        }

    def mostrar_detalle(self):
        return (
            f'{self.titulo} · {self.municipio}. Estado: {self._estado}. '
            f'Inscritos: {self.total_inscritos}.'
        )

    def __str__(self):
        return self.titulo