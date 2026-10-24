from django.contrib import admin

from .models import ContenidoEducativo, Material, PuntoMaterial, PuntoRecepcion


class PuntoMaterialInline(admin.TabularInline):
    """Permite agregar los materiales directamente desde el formulario del punto."""
    model = PuntoMaterial
    extra = 1


@admin.register(PuntoRecepcion)
class PuntoRecepcionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'municipio', 'estado_informacion', 'gestor', 'activo')
    list_filter = ('tipo', 'estado_informacion', 'municipio', 'activo')
    search_fields = ('nombre', 'direccion')
    inlines = [PuntoMaterialInline]
    actions = ['confirmar_informacion']

    @admin.action(description='Confirmar la información de los puntos seleccionados')
    def confirmar_informacion(self, request, queryset):
        for punto in queryset:
            punto.confirmar_informacion()


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('nombre',)


@admin.register(ContenidoEducativo)
class ContenidoEducativoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'material', 'autor', 'publicado', 'fecha_publicacion')
    list_filter = ('publicado',)
    search_fields = ('titulo', 'resumen')
    actions = ['publicar']

    @admin.action(description='Publicar los contenidos seleccionados')
    def publicar(self, request, queryset):
        for contenido in queryset:
            contenido.publicar()