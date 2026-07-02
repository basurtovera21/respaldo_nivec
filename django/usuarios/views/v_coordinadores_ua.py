from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import openpyxl

from usuarios.models import UsuarioDeSistema, PerfilAdministrativo, PerfilDocente
from usuarios.forms import FormularioUsuarioDeSistema, FormularioRegistrarCoordinadorUA, FormularioDatosDocenteUA
from usuarios.utils import (
    generar_identificador_siguiente, requiere_perfil, usuario_es_solo_lectura,
    ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR,
)

from poo.clases.usuarios.usuario_administrativo import UsuarioAdministrativo as UsuarioAdministrativoBase
from poo.clases.enums.perfil_administrativo import PerfilAdministrativo as EnumPerfilAdministrativo
from poo.clases.enums.estado_de_usuario import EstadoDeUsuario
from poo.clases.enums.estado_de_vinculacion import EstadoDeVinculacion

from usuarios.services import servicio_coordinador_ua_registrar_masivo_desde_excel

ROLES_USUARIOS_VEN = (ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR)

@requiere_perfil(*ROLES_USUARIOS_VEN)
def listar_coordinadores_ua(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    coordinadores = PerfilAdministrativo.objects.filter(
        universidad=universidad_usuario,
        perfil_administrativo=EnumPerfilAdministrativo.COORDINADOR_UA.value
    ).select_related("usuario_de_sistema").prefetch_related("usuario_de_sistema__perfil_docente")
    
    return render(request, "usuarios/listar_coordinadores_ua.html", {
        "coordinadores": coordinadores,
        "titulo_pagina": "Coordinador de unidad académica - NIVEC",
        "titulo": "Coordinadores de unidades académicas",
        "url_registrar": "registrar_coordinador_ua",
        "texto_registrar": "Registrar",
        "url_volver": "panel_director_dan",
        "solo_lectura": usuario_es_solo_lectura(request.user),
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def descargar_plantilla_coordinador_ua(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Coordinadores UA"

    cabeceras = [
        "Tipo de identificación (Cédula, Pasaporte, Cédula extranjera)", 
        "Número de identificación", 
        "Nombres",
        "Apellidos", 
        "Correo institucional",
        "Código de Carrera (CAR...)",
        "Tipo de vinculación (Nombramiento, Contrato, Ocasional, Honorario)",
        "Tiempo de dedicación (Tiempo completo, Medio tiempo, Tiempo parcial)",
        "Carga horaria máxima (número decimal)",
        "Especialidades (información separada por comas)",
        "Jornada (Matutina, Vespertina, Nocturna, (continua, información separada por comas)"
    ]
    ws.append(cabeceras)

    for col in range(1, len(cabeceras) + 1): 
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 40

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="formato_coordinador_ua_nivec.xlsx"'
    wb.save(response)
    return response

@requiere_perfil(ROL_DIRECTOR_DAN)
def registrar_coordinador_ua(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    if request.method == "POST":
        if 'archivo_excel' in request.FILES:
            archivo = request.FILES['archivo_excel']
            if not archivo.name.endswith('.xlsx'):
                messages.error(request, "Documento con formato no válido")
                return redirect("registrar_coordinador_ua")
                
            resultado = servicio_coordinador_ua_registrar_masivo_desde_excel(archivo, universidad_usuario)
            
            if resultado["error"]:
                messages.error(request, resultado["error"])
                return redirect("registrar_coordinador_ua")
                
            for advertencia in resultado["advertencias"]:
                messages.warning(request, advertencia)
                
            if resultado["exitosos"] > 0:
                messages.success(request, f"{resultado['exitosos']} Coordinadores de unidad académica registrados correctamente")
            else:
                messages.warning(request, "No se procesaron registros")
                
            return redirect("listar_coordinadores_ua")

        else:
            formulario_usuario = FormularioUsuarioDeSistema(request.POST)
            formulario_perfil = FormularioRegistrarCoordinadorUA(request.POST, universidad=universidad_usuario)
            formulario_docente = FormularioDatosDocenteUA(request.POST) 

            if formulario_usuario.is_valid() and formulario_perfil.is_valid() and formulario_docente.is_valid():
                with transaction.atomic():
                    usuario = formulario_usuario.save(commit=False)
                    usuario.set_password(usuario.identificacion)
                    usuario.save()
                    
                    enum_perfil = EnumPerfilAdministrativo(formulario_perfil.cleaned_data.get('perfil_administrativo'))
                    prefijo = UsuarioAdministrativoBase.definir_prefijo_identificador(enum_perfil)

                    perfil = formulario_perfil.save(commit=False)
                    perfil.usuario_de_sistema = usuario
                    perfil.universidad = universidad_usuario
                    perfil.identificador_administrativo = generar_identificador_siguiente(PerfilAdministrativo, prefijo, 'identificador_administrativo')
                    perfil.identificador_coordinador_ua = generar_identificador_siguiente(PerfilAdministrativo, prefijo, 'identificador_coordinador_ua')
                    perfil.save()

                    docente = formulario_docente.save(commit=False)
                    docente.usuario_de_sistema = usuario
                    docente.universidad = universidad_usuario
                    docente.identificador_institucional = generar_identificador_siguiente(PerfilDocente, "DC", 'identificador_institucional')
                    docente.estado_de_vinculacion = EstadoDeVinculacion.ACTIVO.value
                    docente.especialidades = formulario_docente.cleaned_data.get('especialidades', [])
                    docente.jornadas = formulario_docente.cleaned_data.get('jornadas', [])
                    docente.save()

                messages.success(request, "El Coordinador de unidad académica ha sido registrado correctamente")
                return redirect("listar_coordinadores_ua")
                
    else:
        formulario_usuario = FormularioUsuarioDeSistema()
        formulario_perfil = FormularioRegistrarCoordinadorUA(universidad=universidad_usuario)
        formulario_docente = FormularioDatosDocenteUA()

    return render(request, "usuarios/formulario_administrativo.html", {
        "form_usuario": formulario_usuario,
        "form_perfil": formulario_perfil,
        "form_docente": formulario_docente, 
        "titulo_pagina": "Coordinador de unidad académica - NIVEC",
        "titulo": "Registrar Coordinador de unidad académica",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_coordinadores_ua",
        "mostrar_carga_masiva": True,
        "url_plantilla": "descargar_plantilla_coordinador_ua"
    })