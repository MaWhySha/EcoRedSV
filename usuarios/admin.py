from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Municipio, Organizacion, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Panel de usuarios adaptado al modelo propio (sin first_name ni last_name)."""

    list_display = ('username', 'nombre', 'email', 'rol', 'correo_verificado', 'is_active')
    list_filter = ('rol', 'correo_verificado', 'is_active', 'municipio')
    search_fields = ('username', 'nombre', 'email')
    ordering = ('username',)

    fieldsets = (
        ('Acceso', {'fields': ('username', 'password')}),
        ('Datos personales', {'fields': ('nombre', 'email', 'correo_verificado')}),
        ('Rol y ubicación', {'fields': ('rol', 'municipio', 'organizacion')}),
        ('Permisos de Django', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nombre', 'email', 'rol', 'password1', 'password2'),
        }),
    )


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'departamento')
    search_fields = ('nombre', 'departamento')


@admin.register(Organizacion)
class OrganizacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'correo_contacto', 'telefono_contacto')
    list_filter = ('tipo',)
    search_fields = ('nombre',)