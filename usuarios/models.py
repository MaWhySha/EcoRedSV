from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone

from core.models import EntidadBase
from usuarios.permisos import PERMISOS_POR_ROL, REQUIEREN_CORREO_VERIFICADO
from usuarios.permisos import Rol as RolPermiso


class Municipio(EntidadBase):
    """Zona administrativa para filtrar la información y ampliar el sistema."""

    id_municipio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)

    class Meta:
        db_table = 'municipio'
        ordering = ['departamento', 'nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['nombre', 'departamento'],
                name='uq_municipio_nombre_departamento',
            ),
        ]

    def __str__(self):
        return f'{self.nombre}, {self.departamento}'

    def listar_puntos(self):
        """Puntos de recepción activos del municipio."""
        return self.puntorecepcion_set.filter(activo=True)


class Organizacion(EntidadBase):
    """Institución, centro educativo, alcaldía u ONG que organiza campañas."""

    class Tipo(models.TextChoices):
        CENTRO_EDUCATIVO = 'CENTRO_EDUCATIVO', 'Centro educativo'
        ALCALDIA = 'ALCALDIA', 'Alcaldía'
        ONG = 'ONG', 'ONG'
        EMPRESA = 'EMPRESA', 'Empresa'
        GRUPO_COMUNITARIO = 'GRUPO_COMUNITARIO', 'Grupo comunitario'

    id_organizacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, unique=True)
    tipo = models.CharField(max_length=30, choices=Tipo.choices)
    descripcion = models.CharField('descripción', max_length=500, blank=True)
    correo_contacto = models.EmailField(max_length=254, blank=True)
    telefono_contacto = models.CharField('teléfono de contacto', max_length=20, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organizacion'
        verbose_name = 'organización'
        verbose_name_plural = 'organizaciones'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def listar_campanias(self):
        """Campañas organizadas por esta institución."""
        return self.campanias.all()


class UsuarioManager(UserManager):
    """El superusuario se crea con rol de administrador y correo verificado."""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('rol', Usuario.Rol.ADMIN)
        extra_fields.setdefault('correo_verificado', True)
        return super().create_superuser(username, email, password, **extra_fields)


class Usuario(AbstractUser, EntidadBase):
    """Persona registrada; sus permisos dependen de su rol."""

    class Rol(models.TextChoices):
        COMUNIDAD = 'COMUNIDAD', 'Comunidad'
        GESTOR = 'GESTOR', 'Gestor de residuos'
        ORGANIZACION = 'ORGANIZACION', 'Organización'
        ADMIN = 'ADMIN', 'Administrador'

    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(
        'nombre de usuario',
        max_length=50,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        db_column='nombre_usuario',
    )
    email = models.EmailField('correo', max_length=254, unique=True, db_column='correo')
    password = models.CharField('contraseña', max_length=128, db_column='contrasena')
    first_name = None
    last_name = None
    nombre = models.CharField(max_length=100)
    correo_verificado = models.BooleanField(default=False)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.COMUNIDAD)
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='id_municipio',
        related_name='usuarios',
    )
    organizacion = models.ForeignKey(
        Organizacion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='id_organizacion',
        related_name='usuarios',
    )
    is_active = models.BooleanField('activo', default=True, db_column='activo')
    date_joined = models.DateTimeField('fecha de registro', default=timezone.now, db_column='fecha_registro')

    objects = UsuarioManager()

    REQUIRED_FIELDS = ['email', 'nombre']

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return f'{self.nombre} ({self.get_rol_display()})'

    def get_full_name(self):
        return self.nombre

    def get_short_name(self):
        return self.nombre

    def verificar_correo(self):
        """Marca el correo como verificado (RF-01)."""
        self.correo_verificado = True
        self.save(update_fields=['correo_verificado'])

    def tiene_permiso(self, accion):
        """Indica si el rol del usuario permite una acción."""
        if self.is_superuser:
            return True
        if accion in REQUIEREN_CORREO_VERIFICADO and not self.correo_verificado:
            return False
        return accion in PERMISOS_POR_ROL[RolPermiso(self.rol)]

    def puede_editar(self, objeto):
        """El administrador edita todo; los demás, solo lo que gestionan o crearon."""
        if self.is_superuser or self.rol == self.Rol.ADMIN:
            return True
        responsable = (
            getattr(objeto, 'gestor_id', None)
            or getattr(objeto, 'creador_id', None)
            or getattr(objeto, 'autor_id', None)
        )
        return responsable == self.pk