from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache

from usuarios import services

from usuarios.models import PerfilAdministrativo, PerfilDocente, PerfilEstudiante
from poo.clases.enums.perfil_administrativo import PerfilAdministrativo as EnumPerfilAdministrativo

@never_cache
def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("panel_principal")
    
    if request.method == "POST":
        correo_institucional = request.POST.get("correo_institucional")
        contrasena = request.POST.get("contrasena")
        
        resultado_inicio = services.servicio_iniciar_sesion(request, correo_institucional, contrasena)
        
        if resultado_inicio["exito"]:
            return redirect("panel_principal")

        messages.error(request, resultado_inicio["mensaje"])
    
    return render(request, "autenticacion/iniciar_sesion.html")


@login_required
def cerrar_sesion(request):
    services.servicio_cerrar_sesion(request)
    return redirect("iniciar_sesion")


def panel_sin_perfil(request):
    return render(request, "autenticacion/sin_perfil.html")

@login_required
@never_cache
def panel_principal(request):
    usuario = request.user
    
    perfil_administrativo = PerfilAdministrativo.objects.filter(usuario_de_sistema=usuario).first()
    
    if perfil_administrativo:
        tipo_de_perfil = perfil_administrativo.perfil_administrativo

        if tipo_de_perfil == EnumPerfilAdministrativo.COORDINADOR_UA.value:
            return redirect('panel_ua')
        
        elif tipo_de_perfil == EnumPerfilAdministrativo.DIRECTOR_DAN.value:
            return redirect('panel_director_dan')
            
        elif tipo_de_perfil == EnumPerfilAdministrativo.COORDINADOR_DAN.value:
            return redirect('panel_dan')
            
        else:
            return redirect('panel_administrativo')
            
            
    elif PerfilDocente.objects.filter(usuario_de_sistema=usuario).exists():
        return redirect('panel_docente')
        
    elif PerfilEstudiante.objects.filter(usuario_de_sistema=usuario).exists():
        return redirect('panel_estudiante')
        
    return redirect('sin_perfil')

@login_required
@never_cache
def panel_director_dan(request):
    return render(request, "administrativo/panel_director_dan.html")

@login_required
@never_cache
def panel_dan(request):
    return render(request, "administrativo/panel_dan.html")

@login_required
@never_cache
def panel_ua(request):
    return render(request, "administrativo/panel_ua.html")

@login_required
@never_cache
def panel_administrativo(request):
    return render(request, "administrativo/panel_administrativo.html")

@login_required
@never_cache
def panel_docente(request):
    return render(request, "docente/panel_docente.html")

@login_required
@never_cache
def panel_estudiante(request):
    return render(request, "estudiante/panel_estudiante.html")