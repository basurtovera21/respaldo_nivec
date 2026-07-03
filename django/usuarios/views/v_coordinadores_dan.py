from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import openpyxl

from usuarios.models import UsuarioDeSistema, PerfilAdministrativo
from usuarios.forms import FormularioUsuarioDeSistema, FormularioRegistrarCoordinadorDAN
from usuarios.utils import (
    generar_identificador_siguiente, requiere_perfil, usuario_es_solo_lectura,
    ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN, ROL_RECTOR, ROL_VICERRECTOR,
)

from poo.clases.enums.estado_de_usuario import EstadoDeUsuario as EnumEstadoDeUsuario
from poo.clases.enums.perfil_administrativo import PerfilAdministrativo as EnumPerfilAdministrativo
from poo.clases.usuarios.usuario_administrativo import UsuarioAdministrativo as UsuarioAdministrativoBase

from usuarios.services import servicio_coordinador_dan_registrar_masivo_desde_excel

ROLES_USUARIOS_VEN = (ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN, ROL_RECTOR, ROL_VICERRECTOR)

@requiere_perfil(*ROLES_USUARIOS_VEN)
def listar_coordinadores_dan(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    coordinadores = PerfilAdministrativo.objects.filter(
        universidad=universidad_usuario,
        perfil_administrativo=EnumPerfilAdministrativo.COORDINADOR_DAN.value
    ).select_related("usuario_de_sistema")

    busqueda = request.GET.get("busqueda", "").strip()
    if busqueda:
        from django.db.models import Q
        coordinadores = coordinadores.filter(
            Q(usuario_de_sistema__nombres__icontains=busqueda) |
            Q(usuario_de_sistema__apellidos__icontains=busqueda)
        )

    coordinadores = coordinadores.order_by("-identificador_coordinador_dan")

    return render(request, "usuarios/listar_coordinadores_dan.html", {
        "coordinadores": coordinadores,
        "busqueda": busqueda,
        "titulo_pagina": "Coordinador de dirección de admisión y nivelación - NIVEC",
        "titulo": "Coordinadores de dirección de admisión y nivelación",
        "url_registrar": "registrar_coordinador_dan",
        "texto_registrar": "Registrar",
        "url_volver": "panel_director_dan",
        "solo_lectura": usuario_es_solo_lectura(request.user),
    })

@requiere_perfil(ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN)
def descargar_plantilla_coordinador_dan(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Coordinadores DAN"

    cabeceras = [
        "Tipo de identificación (Cédula, Pasaporte, Cédula extranjera)", 
        "Número de identificación", 
        "Nombres",
        "Apellidos", 
        "Correo institucional"
    ]
    ws.append(cabeceras)

    for col in range(1, len(cabeceras) + 1): 
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 40

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="formato_coordinador_dan_nivec.xlsx"'
    wb.save(response)
    return response

@requiere_perfil(ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN)
def registrar_coordinador_dan(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    if request.method == "POST":
        if 'archivo_excel' in request.FILES:
            archivo = request.FILES['archivo_excel']
            if not archivo.name.endswith('.xlsx'):
                messages.error(request, "Documento con formato no válido")
                return redirect("registrar_coordinador_dan")

            resultado = servicio_coordinador_dan_registrar_masivo_desde_excel(archivo, universidad_usuario)
            
            if resultado["error"]:
                messages.error(request, resultado["error"])
                return redirect("registrar_coordinador_dan")
                
            for advertencia in resultado["advertencias"]:
                messages.warning(request, advertencia)
                
            if resultado["exitosos"] > 0:
                messages.success(request, f"{resultado['exitosos']} Coordinadores de dirección de admisión y nivelación registrados correctamente")
            else:
                messages.warning(request, "No se procesaron registros")
                
            return redirect("listar_coordinadores_dan")

        else:
            formulario_usuario = FormularioUsuarioDeSistema(request.POST)
            formulario_perfil = FormularioRegistrarCoordinadorDAN(request.POST)

            if formulario_usuario.is_valid() and formulario_perfil.is_valid():
                with transaction.atomic():
                    usuario = formulario_usuario.save(commit=False)
                    usuario.set_password(usuario.identificacion)
                    usuario.save()
                    
                    perfil = formulario_perfil.save(commit=False)
                    perfil.perfil_administrativo = EnumPerfilAdministrativo.COORDINADOR_DAN.value
                    perfil.usuario_de_sistema = usuario
                    perfil.universidad = universidad_usuario
                    
                    enum_perfil = EnumPerfilAdministrativo(perfil.perfil_administrativo)
                    prefijo = UsuarioAdministrativoBase.definir_prefijo_identificador(enum_perfil)
                    
                    perfil.identificador_administrativo = generar_identificador_siguiente(
                        PerfilAdministrativo, prefijo, 'identificador_administrativo'
                    )
                    perfil.identificador_coordinador_dan = generar_identificador_siguiente(
                        PerfilAdministrativo, prefijo, 'identificador_coordinador_dan'
                    )
                    perfil.save()
                
                messages.success(request, "El Coordinador de dirección de admisión y nivelación ha sido registrado correctamente")
                return redirect("listar_coordinadores_dan")
            
    else:
        formulario_usuario = FormularioUsuarioDeSistema()
        formulario_perfil = FormularioRegistrarCoordinadorDAN()

    return render(request, "usuarios/formulario_administrativo.html", {
        "form_usuario": formulario_usuario,
        "form_perfil": formulario_perfil,
        "titulo_pagina": "Coordinador de dirección de admisión y nivelación - NIVEC",
        "titulo": "Registrar Coordinador de dirección de admisión y nivelación",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_coordinadores_dan",
        "mostrar_carga_masiva": True,
        "url_plantilla": "descargar_plantilla_coordinador_dan"
    })