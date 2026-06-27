from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import openpyxl

from usuarios.models import UsuarioDeSistema, PerfilDocente, PerfilAdministrativo
from usuarios.forms import FormularioUsuarioDeSistema, FormularioRegistrarDocente
from usuarios.utils import generar_identificador_siguiente
from usuarios.services import servicio_docente_registrar_masivo_desde_excel, _crear_docente

from poo.clases.enums.estado_de_usuario import EstadoDeUsuario as EnumEstadoDeUsuario
from poo.clases.enums.estado_de_vinculacion import EstadoDeVinculacion as EnumEstadoDeVinculacion
from poo.clases.servicios.centro_de_operacion_academica import CentroDeOperacionAcademica

@login_required
def listar_docentes(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    docentes = PerfilDocente.objects.filter(universidad=universidad_usuario).select_related("usuario_de_sistema")
    
    return render(request, "usuarios/listar_docentes.html", {
        "docentes": docentes,
        "titulo_pagina": "Docente - NIVEC",
        "titulo": "Docentes",
        "url_registrar": "registrar_docente",
        "texto_registrar": "Registrar",
        "url_volver": "panel_principal"
    })

@login_required
def descargar_plantilla_docente(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Docentes"
    cabeceras = ["Tipo de identificación (Cédula, Pasaporte, Cédula extranjera)", "Número de identificación", "Nombres", "Apellidos", "Correo institucional", "Tipo de vinculación (Nombramiento, Contrato, Ocasional, Honorario)", "Tiempo de dedicación (Tiempo completo, Medio tiempo, Tiempo parcial)", "Carga horaria máxima (número decimal)", "Especialidades (información separada por comas)"]
    ws.append(cabeceras)
    for col in range(1, len(cabeceras) + 1): 
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 40

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="formato_docentes_nivec.xlsx"'
    wb.save(response)
    return response

@login_required
def registrar_docente(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    if request.method == "POST":
        if 'archivo_excel' in request.FILES:
            archivo = request.FILES['archivo_excel']
            if not archivo.name.endswith('.xlsx'):
                messages.error(request, "Documento con formato no válido")
                return redirect("registrar_docente")
            
            resultado = servicio_docente_registrar_masivo_desde_excel(archivo, universidad_usuario)
            
            if resultado["error"]: messages.error(request, resultado["error"])
            for adv in resultado["advertencias"]: messages.warning(request, adv)
            if resultado["exitosos"] > 0: messages.success(request, f"{resultado['exitosos']} Docentes registrados correctamente")
            return redirect("listar_docentes")
                
        else:
            formulario_usuario = FormularioUsuarioDeSistema(request.POST)
            formulario_docente = FormularioRegistrarDocente(request.POST) 

            if formulario_usuario.is_valid() and formulario_docente.is_valid():
                with transaction.atomic():
                    usuario = formulario_usuario.save(commit=False)
                    usuario.set_password(usuario.identificacion)
                    usuario.save()
                    
                    docente = formulario_docente.save(commit=False)
                    docente.usuario_de_sistema = usuario
                    docente.identificador_institucional = generar_identificador_siguiente(PerfilDocente, "DC", 'identificador_institucional')
                    docente.estado_de_vinculacion = EnumEstadoDeVinculacion.ACTIVO.value
                    docente.universidad = universidad_usuario
                    docente.especialidades = formulario_docente.cleaned_data.get('especialidades', [])
                    docente.save()

                messages.success(request, "El Docente ha sido registrado correctamente")
                return redirect("listar_docentes")
    else:
        formulario_usuario = FormularioUsuarioDeSistema()
        formulario_docente = FormularioRegistrarDocente()

    return render(request, "usuarios/formulario_docente.html", {
        "form_usuario": formulario_usuario,
        "form_docente": formulario_docente,
        "titulo_pagina": "Docente - NIVEC",
        "titulo": "Registrar Docente",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_docentes",
        "mostrar_carga_masiva": True,
        "url_plantilla": "descargar_plantilla_docente"
    })


@login_required
def modificar_docente(request, docente_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    docente = get_object_or_404(PerfilDocente, id=docente_id, universidad=universidad_usuario)
    usuario = docente.usuario_de_sistema

    if request.method == "POST":
        formulario_usuario = FormularioUsuarioDeSistema(request.POST, instance=usuario)
        formulario_docente = FormularioRegistrarDocente(request.POST, instance=docente)

        if 'contrasena' in formulario_usuario.fields:
            formulario_usuario.fields['contrasena'].required = False

        if formulario_usuario.is_valid() and formulario_docente.is_valid():
            with transaction.atomic():
                usuario_guardado = formulario_usuario.save(commit=False)
                if formulario_usuario.cleaned_data.get('contrasena'):
                    usuario_guardado.set_password(formulario_usuario.cleaned_data.get('contrasena'))
                usuario_guardado.save()
                
                docente_guardado = formulario_docente.save(commit=False)
                docente_guardado.especialidades = formulario_docente.cleaned_data.get('especialidades', [])
                docente_guardado.save()

            messages.success(request, "El docente ha sido modificado correctamente")
            return redirect("listar_docentes")
    else:
        formulario_usuario = FormularioUsuarioDeSistema(instance=usuario)
        formulario_docente = FormularioRegistrarDocente(instance=docente)

    return render(request, "usuarios/formulario_docente.html", {
        "form_usuario": formulario_usuario,
        "form_docente": formulario_docente, 
        "titulo_pagina": "Docente - NIVEC",
        "titulo": "Modificar Docente",
        "subtitulo": f"{usuario.nombres} {usuario.apellidos}",
        "boton_texto": "Modificar",
        "url_cancelar": "listar_docentes",
        "url_volver": "listar_docentes",
        "mostrar_carga_masiva": False
    })

@login_required
def eliminar_docente(request, docente_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    docente = get_object_or_404(PerfilDocente, id=docente_id, universidad=universidad_usuario)
    try:
        with transaction.atomic():
            docente.usuario_de_sistema.delete()
        messages.success(request, "El Docente ha sido eliminado correctamente")
    except Exception:
        messages.error(request, "No se ha podido eliminar al Docente")
    return redirect("listar_docentes")

@login_required
def inhabilitar_docente(request, docente_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    docente_db = get_object_or_404(PerfilDocente, id=docente_id, universidad=universidad_usuario)
    
    docente_poo = _crear_docente(docente_db)
    facade = CentroDeOperacionAcademica()
    facade.inhabilitar_docente(docente_poo)

    with transaction.atomic():
        docente_db.estado_de_vinculacion = EnumEstadoDeVinculacion.INACTIVO.value
        docente_db.save()
        usuario = docente_db.usuario_de_sistema
        usuario.estado_de_usuario = EnumEstadoDeUsuario.INACTIVO.value
        usuario.is_active = False
        usuario.save()

    messages.success(request, "El Docente ha sido inhabilitado correctamente")
    return redirect("listar_docentes")

@login_required
def habilitar_docente(request, docente_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    docente_db = get_object_or_404(PerfilDocente, id=docente_id, universidad=universidad_usuario)
    
    docente_poo = _crear_docente(docente_db)
    facade = CentroDeOperacionAcademica()
    facade.habilitar_docente(docente_poo)

    with transaction.atomic():
        docente_db.estado_de_vinculacion = EnumEstadoDeVinculacion.ACTIVO.value
        docente_db.save()
        usuario = docente_db.usuario_de_sistema
        usuario.estado_de_usuario = EnumEstadoDeUsuario.ACTIVO.value
        usuario.is_active = True
        usuario.save()

    messages.success(request, "El Docente ha sido habilitado correctamente")
    return redirect("listar_docentes")