from django.shortcuts import render, redirect
from django.contrib import messages
from usuarios.utils import requiere_perfil, ROL_DIRECTOR_DAN
from academico.forms import FormularioUniversidad

@requiere_perfil(ROL_DIRECTOR_DAN)
def detalle_universidad(request):
    universidad = request.user.perfil_administrativo.universidad
    if not universidad:
        return redirect("registrar_universidad")
        
    return render(request, "entidades/detalle_universidad.html", {
        "universidad": universidad,
        "titulo_pagina": "Universidad - NIVEC"
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def registrar_universidad(request):
    if request.user.perfil_administrativo.universidad:
        return redirect("panel_principal")

    if request.method == "POST":
        formulario_universidad = FormularioUniversidad(request.POST, request.FILES)
        if formulario_universidad.is_valid():
            nueva_universidad = formulario_universidad.save()
            perfil = request.user.perfil_administrativo
            perfil.universidad = nueva_universidad
            perfil.save()
            
            messages.success(request, "La Universidad ha sido registrada correctamente")
            return redirect("panel_principal")
    else:
        formulario_universidad = FormularioUniversidad()
        
    return render(request, "entidades/formulario_universidad.html", {
        "formulario": formulario_universidad,
        "titulo_pagina": "Universidad - NIVEC",
        "titulo": "Registrar universidad",
        "boton_texto": "Registrar",
        "url_cancelar": "panel_principal",
        "mostrar_carga_masiva": False
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def modificar_universidad(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("registrar_universidad")

    if request.method == "POST":
        formulario = FormularioUniversidad(request.POST, request.FILES, instance=universidad_usuario)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "La Universidad ha sido modificada correctamente")
            return redirect("detalle_universidad")
    else:
        formulario = FormularioUniversidad(instance=universidad_usuario)
        
    return render(request, "entidades/formulario_universidad.html", {
        "formulario": formulario,
        "titulo_pagina": "Universidad - NIVEC",
        "titulo": "Modificar universidad",
        "boton_texto": "Modificar",
        "url_cancelar": "detalle_universidad",
        "mostrar_carga_masiva": False
    })
