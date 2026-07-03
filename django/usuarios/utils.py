from functools import wraps

from django.db.models import Max
from django.contrib import messages
from django.shortcuts import redirect
import re

from poo.clases.enums.perfil_administrativo import PerfilAdministrativo as EnumPerfilAdministrativo

def generar_identificador_siguiente(modelo, prefijo, nombre_campo):
    resultado_agregado = modelo.objects.filter(
        **{f"{nombre_campo}__startswith": prefijo}
    ).aggregate(Max(nombre_campo))

    identificador_maximo = resultado_agregado[f"{nombre_campo}__max"]

    if identificador_maximo:
        correlativo_actual = int(re.search(r'\d+', identificador_maximo).group())
        siguiente_correlativo = correlativo_actual + 1
    else:
        siguiente_correlativo = 1

    return f"{prefijo}{siguiente_correlativo:03d}"

ROL_RECTOR = EnumPerfilAdministrativo.RECTOR.value
ROL_VICERRECTOR = EnumPerfilAdministrativo.VICERRECTOR_ACADEMICO.value
ROL_DIRECTOR_DAN = EnumPerfilAdministrativo.DIRECTOR_DAN.value
ROL_COORDINADOR_DAN = EnumPerfilAdministrativo.COORDINADOR_DAN.value
ROL_COORDINADOR_UA = EnumPerfilAdministrativo.COORDINADOR_UA.value
ROL_DOCENTE = "DOCENTE"
ROL_ESTUDIANTE = "ESTUDIANTE"
ROLES_SOLO_LECTURA = (ROL_RECTOR, ROL_VICERRECTOR)

def obtener_rol_usuario(usuario):
    from usuarios.models import PerfilAdministrativo, PerfilDocente, PerfilEstudiante

    if not usuario or not usuario.is_authenticated:
        return None

    perfil_administrativo = PerfilAdministrativo.objects.filter(usuario_de_sistema=usuario).first()
    if perfil_administrativo:
        return perfil_administrativo.perfil_administrativo

    if PerfilDocente.objects.filter(usuario_de_sistema=usuario).exists():
        return ROL_DOCENTE

    if PerfilEstudiante.objects.filter(usuario_de_sistema=usuario).exists():
        return ROL_ESTUDIANTE

    return None

def usuario_es_solo_lectura(usuario):
    return obtener_rol_usuario(usuario) in ROLES_SOLO_LECTURA

def requiere_perfil(*roles_permitidos):
    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("iniciar_sesion")

            rol = obtener_rol_usuario(request.user)

            if rol is None:
                return redirect("cerrar_sesion")

            if rol not in roles_permitidos:
                messages.error(request, "No tiene permisos para acceder a esta sección.")
                return redirect("panel_principal")

            return vista(request, *args, **kwargs)
        return envoltura
    return decorador