from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegistroForm


def registro(request):

    if request.user.is_authenticated:
        return redirect("core:inicio")

    if request.method == "POST":
        form = RegistroForm(request.POST)

        if form.is_valid():
            usuario = form.save()
            login(request, usuario)

            messages.success(
                request,
                "Tu cuenta se creó correctamente. ¡Bienvenido a EcoRedSV!"
            )

            return redirect("core:inicio")

    else:
        form = RegistroForm()

    return render(
        request,
        "usuarios/registro.html",
        {"form": form}
    )