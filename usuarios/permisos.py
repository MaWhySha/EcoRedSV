from enum import Enum


class Rol(Enum):
    """Roles del sistema definidos en la Semana 3."""
    COMUNIDAD = 'COMUNIDAD'
    GESTOR = 'GESTOR'
    ORGANIZACION = 'ORGANIZACION'
    ADMIN = 'ADMIN'


class Accion(Enum):
    """Acciones que requieren permiso."""
    REPORTAR = 'reportar'
    APOYAR = 'apoyar'
    COMENTAR = 'comentar'
    INSCRIBIRSE = 'inscribirse'
    ACTUALIZAR_PUNTO = 'actualizar_punto'
    REGISTRAR_CAMPANIA = 'registrar_campania'
    REGISTRAR_PESO = 'registrar_peso'
    GESTIONAR_REPORTES = 'gestionar_reportes'
    MODERAR = 'moderar'
    PUBLICAR_CONTENIDO = 'publicar_contenido'


# Cada rol tiene los permisos del anterior más los suyos (sección 3.4)
_PERMISOS_COMUNIDAD = {
    Accion.REPORTAR, Accion.APOYAR, Accion.COMENTAR, Accion.INSCRIBIRSE,
}
_PERMISOS_GESTOR = _PERMISOS_COMUNIDAD | {Accion.ACTUALIZAR_PUNTO}
_PERMISOS_ORGANIZACION = _PERMISOS_GESTOR | {
    Accion.REGISTRAR_CAMPANIA, Accion.REGISTRAR_PESO,
}

PERMISOS_POR_ROL = {
    Rol.COMUNIDAD: _PERMISOS_COMUNIDAD,
    Rol.GESTOR: _PERMISOS_GESTOR,
    Rol.ORGANIZACION: _PERMISOS_ORGANIZACION,
    Rol.ADMIN: set(Accion),
}

# Acciones que exigen correo verificado (RF-01)
REQUIEREN_CORREO_VERIFICADO = {
    Accion.REPORTAR, Accion.APOYAR, Accion.COMENTAR, Accion.INSCRIBIRSE,
}


class PerfilUsuario:
    """Datos de acceso de un usuario y control de sus permisos."""

    def __init__(self, nombre_usuario, rol, correo_verificado=False):
        self.nombre_usuario = nombre_usuario
        self.rol = rol
        self.correo_verificado = correo_verificado

    def verificar_correo(self):
        self.correo_verificado = True

    def tiene_permiso(self, accion):
        """Indica si el rol del usuario permite realizar una acción."""
        if accion in REQUIEREN_CORREO_VERIFICADO and not self.correo_verificado:
            return False
        return accion in PERMISOS_POR_ROL[self.rol]

    def puede_editar(self, objeto):
        """
        Verifica si puede modificar un registro concreto.
        El administrador puede editar todo; los demás, solo lo que gestionan o crearon.
        """
        if self.rol == Rol.ADMIN:
            return True
        responsable = getattr(objeto, 'gestor', None) or getattr(objeto, 'creador', None)
        return responsable == self.nombre_usuario

    def __str__(self):
        return f'{self.nombre_usuario} ({self.rol.value})'