from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import EntidadBase, Ubicable


class Material(EntidadBase):
    """Tipo de material reciclable y cómo prepararlo para entregarlo."""

    class Categoria(models.TextChoices):
        PLASTICO = 'PLASTICO', 'Plástico'
        PAPEL_CARTON = 'PAPEL_CARTON', 'Papel y cartón'
        METAL = 'METAL', 'Metal'
        VIDRIO = 'VIDRIO', 'Vidrio'
        ELECTRONICO = 'ELECTRONICO', 'Electrónico'
        ORGANICO = 'ORGANICO', 'Orgánico'
        OTRO = 'OTRO', 'Otro'

    id_material = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80, unique=True)
    categoria = models.CharField('categoría', max_length=30, choices=Categoria.choices)
    descripcion = models.CharField('descripción', max_length=300, blank=True)
    indicaciones = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'material'
        verbose_name_plural = 'materiales'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def puntos_que_lo_reciben(self):
        """Puntos activos que reciben este material (base del filtro RF-05)."""
        return self.puntos.filter(activo=True)

    def mostrar_detalle(self):
        indicaciones = self.indicaciones or 'Sin indicaciones registradas'
        return f'{self.nombre} ({self.get_categoria_display()}). {indicaciones}.'


class PuntoRecepcion(Ubicable):
    """Lugar donde se entregan materiales reciclables."""

    class Tipo(models.TextChoices):
        CENTRO_ACOPIO = 'CENTRO_ACOPIO', 'Centro de acopio'
        GESTOR = 'GESTOR', 'Gestor'
        PUNTO_RECEPCION = 'PUNTO_RECEPCION', 'Punto de recepción'
        INICIATIVA = 'INICIATIVA', 'Iniciativa de reciclaje'
        COMPOSTERA = 'COMPOSTERA', 'Compostera'
        OTRO = 'OTRO', 'Otro'

    class EstadoInformacion(models.TextChoices):
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        POR_CONFIRMAR = 'POR_CONFIRMAR', 'Por confirmar'

    id_punto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=30, choices=Tipo.choices)
    horario = models.CharField(max_length=200, blank=True)
    condiciones_entrega = models.CharField('condiciones de entrega', max_length=500, blank=True)
    telefono_contacto = models.CharField('teléfono de contacto', max_length=20, blank=True)
    estado_informacion = models.CharField(
        'estado de la información',
        max_length=20,
        choices=EstadoInformacion.choices,
        default=EstadoInformacion.POR_CONFIRMAR,
    )
    gestor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_gestor',
        related_name='puntos_gestionados',
    )
    materiales = models.ManyToManyField(
        Material,
        through='PuntoMaterial',
        related_name='puntos',
        blank=True,
    )
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'punto_recepcion'
        verbose_name = 'punto de recepción'
        verbose_name_plural = 'puntos de recepción'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def agregar_material(self, material, observaciones=''):
        """Agrega un material; no puede repetirse en el mismo punto."""
        if self.recibe(material):
            raise ValueError(f'{self.nombre} ya recibe {material.nombre}.')
        return PuntoMaterial.objects.create(punto=self, material=material, observaciones=observaciones)

    def quitar_material(self, material):
        PuntoMaterial.objects.filter(punto=self, material=material).delete()

    def recibe(self, material):
        return self.materiales.filter(pk=material.pk).exists()

    def confirmar_informacion(self):
        """Marca la información del punto como verificada (RF-19)."""
        self.estado_informacion = self.EstadoInformacion.CONFIRMADA
        self.save(update_fields=['estado_informacion', 'actualizado_en'])

    def obtener_marcador(self):
        return {
            'tipo': 'punto',
            'titulo': self.nombre,
            'icono': self.tipo,
            'latitud': float(self.latitud),
            'longitud': float(self.longitud),
        }

    def mostrar_detalle(self):
        materiales = ', '.join(m.nombre for m in self.materiales.all()) or 'Sin materiales registrados'
        return (
            f'{self.nombre} ({self.get_tipo_display()}) · {self.municipio}. '
            f'Recibe: {materiales}. Información: {self.get_estado_informacion_display()}.'
        )


class PuntoMaterial(EntidadBase):
    """Qué material recibe cada punto y con qué condición."""

    id_punto_material = models.AutoField(primary_key=True)
    punto = models.ForeignKey(
        PuntoRecepcion,
        on_delete=models.CASCADE,
        db_column='id_punto',
        related_name='detalles_materiales',
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        db_column='id_material',
        related_name='detalles_puntos',
    )
    observaciones = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'punto_material'
        verbose_name = 'material por punto'
        verbose_name_plural = 'materiales por punto'
        constraints = [
            models.UniqueConstraint(fields=['punto', 'material'], name='uq_punto_material'),
        ]

    def __str__(self):
        return f'{self.punto} · {self.material}'

    def describir(self):
        """Material con su condición particular, si la tiene."""
        if self.observaciones:
            return f'{self.material} ({self.observaciones})'
        return str(self.material)


class ContenidoEducativo(EntidadBase):
    """Información sobre cómo separar, clasificar y preparar los residuos."""

    id_contenido = models.AutoField(primary_key=True)
    titulo = models.CharField('título', max_length=150)
    resumen = models.CharField(max_length=300)
    contenido = models.TextField()
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='id_material',
        related_name='contenidos',
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='id_autor',
        related_name='contenidos_educativos',
    )
    publicado = models.BooleanField(default=False)
    fecha_publicacion = models.DateTimeField('fecha de publicación', null=True, blank=True)

    class Meta:
        db_table = 'contenido_educativo'
        verbose_name = 'contenido educativo'
        verbose_name_plural = 'contenidos educativos'
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo

    def publicar(self):
        """Hace visible el contenido y registra la fecha de publicación."""
        self.publicado = True
        self.fecha_publicacion = timezone.now()
        self.save(update_fields=['publicado', 'fecha_publicacion'])