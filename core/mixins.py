from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect


class PermisoRolMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Exige iniciar sesión y que el rol del usuario permita la acción indicada.
    Cada vista define su atributo 'accion' (por ejemplo, Accion.REPORTAR).
    """

    accion = None

    def test_func(self):
        return self.accion is None or self.request.user.tiene_permiso(self.accion)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Su usuario no tiene permiso para realizar esta acción.')
            return redirect('core:inicio')
        return super().handle_no_permission()


class PuedeEditarMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Solo el administrador o el responsable del registro pueden modificarlo o eliminarlo."""

    def test_func(self):
        return self.request.user.puede_editar(self.get_object())

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Solo el responsable del registro o un administrador pueden modificarlo.')
            return redirect(self.get_object().get_absolute_url())
        return super().handle_no_permission()


class EliminarConProteccionMixin:
    """Si el registro tiene datos asociados protegidos, muestra un aviso en lugar de un error."""

    mensaje_exito = 'El registro se eliminó correctamente.'

    def form_valid(self, form):
        try:
            respuesta = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f'No se puede eliminar «{self.object}» porque tiene registros asociados.',
            )
            return redirect(self.object.get_absolute_url())
        messages.success(self.request, self.mensaje_exito)
        return respuesta