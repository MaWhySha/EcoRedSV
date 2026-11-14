from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class RegistroForm(UserCreationForm):

    class Meta:
        model = Usuario
        fields = ("username", "nombre", "email")

    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.rol = Usuario.Rol.COMUNIDAD
        usuario.correo_verificado = False
        usuario.is_staff = False
        usuario.is_superuser = False
        usuario.is_active = True

        if commit:
            usuario.save()
            self.save_m2m()

        return usuario