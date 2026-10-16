from django.utils import timezone

from core.base import EntidadBase, Ubicable
from usuarios.permisos import Accion


class SeguimientoReporte(EntidadBase):
    """Registro de un cambio de estado: quién, cuándo y por qué."""

    def __init__(self, estado_anterior, estado_nuevo, responsable, comentario=''):
        super().__init__()
        self.estado_anterior = estado_anterior
        self.estado_nuevo = estado_nuevo
        self.responsable = responsable
        self.comentario = comentario
        self.fecha = timezone.now()

    def validar(self):
        if self.estado_anterior == self.estado_nuevo:
            raise ValueError('El estado nuevo debe ser distinto al anterior.')


class Comentario(EntidadBase):
    """Comentario de un usuario sobre un reporte (RF-21)."""

    def __init__(self, usuario, texto):
        super().__init__()
        self.usuario = usuario
        self.texto = texto
        self.visible = True
        self.fecha = timezone.now()

    def ocultar(self):
        self.visible = False

    def validar(self):
        if not self.texto.strip():
            raise ValueError('El comentario no puede estar vacío.')


class ReporteAmbiental(Ubicable):
    """Problema ambiental reportado por un usuario."""

    RECIBIDO = 'RECIBIDO'
    EN_REVISION = 'EN_REVISION'
    ATENDIDO = 'ATENDIDO'
    DESCARTADO = 'DESCARTADO'

    TRANSICIONES = {
        RECIBIDO: {EN_REVISION, DESCARTADO},
        EN_REVISION: {ATENDIDO, DESCARTADO},
        ATENDIDO: set(),
        DESCARTADO: set(),
    }

    GRAVEDADES = ('BAJA', 'MEDIA', 'ALTA')

    def __init__(self, titulo, descripcion, gravedad, direccion, latitud,
                 longitud, municipio, autor):
        super().__init__(direccion, latitud, longitud, municipio)
        self.titulo = titulo
        self.descripcion = descripcion
        self.gravedad = gravedad
        self.autor = autor
        self.visible = True
        self._estado = self.RECIBIDO
        self._seguimiento = []
        self._apoyos = set()  # nombres de usuario; cada uno apoya una sola vez
        self.comentarios = []

    @property
    def estado(self):
        return self._estado

    @property
    def historial(self):
        return list(self._seguimiento)

    @property
    def total_apoyos(self):
        return len(self._apoyos)

    def cambiar_estado(self, nuevo, perfil, comentario=''):
        """Valida el cambio y deja constancia en el historial (RF-11)."""
        if not perfil.tiene_permiso(Accion.GESTIONAR_REPORTES):
            raise PermissionError('El usuario no puede gestionar reportes.')
        if nuevo not in self.TRANSICIONES[self._estado]:
            raise ValueError(f'No se puede pasar de {self._estado} a {nuevo}.')
        seguimiento = SeguimientoReporte(self._estado, nuevo, perfil.nombre_usuario, comentario)
        seguimiento.validar()
        self._seguimiento.append(seguimiento)
        self._estado = nuevo

    def apoyar(self, perfil):
        """Un usuario apoya el reporte una sola vez (RF-20)."""
        if not perfil.tiene_permiso(Accion.APOYAR):
            raise PermissionError('El usuario no puede apoyar (¿correo verificado?).')
        if perfil.nombre_usuario in self._apoyos:
            raise ValueError('El usuario ya apoyó este reporte.')
        self._apoyos.add(perfil.nombre_usuario)

    def comentar(self, perfil, texto):
        """Agrega un comentario validado (RF-21)."""
        if not perfil.tiene_permiso(Accion.COMENTAR):
            raise PermissionError('El usuario no puede comentar (¿correo verificado?).')
        comentario = Comentario(perfil.nombre_usuario, texto)
        comentario.validar()
        self.comentarios.append(comentario)
        return comentario

    def ocultar(self, perfil):
        """Moderación: oculta el reporte sin borrarlo (RF-22)."""
        if not perfil.tiene_permiso(Accion.MODERAR):
            raise PermissionError('Solo el administrador puede moderar.')
        self.visible = False

    def validar(self):
        super().validar()
        if self.gravedad not in self.GRAVEDADES:
            raise ValueError(f'Gravedad no válida: {self.gravedad}.')
        if not self.titulo.strip():
            raise ValueError('El reporte debe tener un título.')

    def obtener_marcador(self):
        return {
            'tipo': 'reporte',
            'titulo': self.titulo,
            'icono': f'alerta-{self.gravedad.lower()}',
            'latitud': self.latitud,
            'longitud': self.longitud,
        }

    def mostrar_detalle(self):
        return (
            f'{self.titulo} · {self.municipio}. Gravedad: {self.gravedad}. '
            f'Estado: {self._estado}. Apoyos: {self.total_apoyos}.'
        )

    def __str__(self):
        return self.titulo


def ordenar_por_apoyos(reportes):
    """Reportes visibles, primero los que tienen más apoyos (RF-20)."""
    visibles = [reporte for reporte in reportes if reporte.visible]
    return sorted(visibles, key=lambda reporte: reporte.total_apoyos, reverse=True)