from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import openpyxl

from usuarios.models import UsuarioDeSistema, PerfilAdministrativo
from usuarios.forms import (
    FormularioUsuarioDeSistema, FormularioModificarUsuarioDeSistema, 
    FormularioRegistrarPerfilAdministrativo, FormularioModificarPerfilAdministrativo, FormularioDatosDocenteUA
)
from usuarios.utils import (
    generar_identificador_siguiente, requiere_perfil, usuario_es_solo_lectura,
    ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN, ROL_RECTOR, ROL_VICERRECTOR,
)

from poo.clases.enums.estado_de_usuario import EstadoDeUsuario as EnumEstadoDeUsuario
from poo.clases.enums.perfil_administrativo import PerfilAdministrativo as EnumPerfilAdministrativo
from poo.clases.usuarios.usuario_administrativo import UsuarioAdministrativo as UsuarioAdministrativoBase
from poo.clases.usuarios.usuario_de_sistema import UsuarioDeSistema as UsuarioDeSistemaBase

from usuarios.services import _crear_usuario_administrativo, servicio_administrativo_registrar_masivo_desde_excel

ROLES_USUARIOS_VEN = (ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN, ROL_RECTOR, ROL_VICERRECTOR)

@requiere_perfil(*ROLES_USUARIOS_VEN)
def listar_administrativos(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    administrativos = PerfilAdministrativo.objects.filter(
        universidad=universidad_usuario
    ).exclude(
        perfil_administrativo__in=[
            EnumPerfilAdministrativo.COORDINADOR_DAN.value,
            EnumPerfilAdministrativo.COORDINADOR_UA.value
        ]
    ).select_related("usuario_de_sistema")

    busqueda = request.GET.get("busqueda", "").strip()
    if busqueda:
        from django.db.models import Q
        administrativos = administrativos.filter(
            Q(usuario_de_sistema__nombres__icontains=busqueda) |
            Q(usuario_de_sistema__apellidos__icontains=busqueda)
        )

    perfil_filtro = request.GET.get("perfil", "").strip()
    perfiles_disponibles = list(
        administrativos.values_list("perfil_administrativo", flat=True).distinct()
    )
    if perfil_filtro:
        administrativos = administrativos.filter(perfil_administrativo=perfil_filtro)

    # Order: Director DAN first, then by identificador_administrativo descending
    from django.db.models import Case, When, Value, IntegerField
    administrativos = administrativos.annotate(
        es_director=Case(
            When(perfil_administrativo=EnumPerfilAdministrativo.DIRECTOR_DAN.value, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by("es_director", "-identificador_administrativo")

    return render(request, "usuarios/listar_administrativos.html", {
        "administrativos": administrativos,
        "busqueda": busqueda,
        "perfil_filtro": perfil_filtro,
        "perfiles_disponibles": perfiles_disponibles,
        "titulo_pagina": "Administrativo - NIVEC",
        "titulo": "Administrativos",
        "url_registrar": "registrar_administrativo",
        "texto_registrar": "Registrar",
        "url_volver": "panel_principal",
        "solo_lectura": usuario_es_solo_lectura(request.user),
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def descargar_plantilla_administrativo(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Administrativos"

    cabeceras = [
        "Tipo de identificación (Cédula, Pasaporte, Cédula extranjera)", 
        "Número de identificación", "Nombres", "Apellidos", 
        "Correo institucional", "Perfil administrativo (Rector, Vicerrector académico)"
    ]
    ws.append(cabeceras)

    for col in range(1, len(cabeceras) + 1): 
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 40

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="administrativos_documento_nivec.xlsx"'
    wb.save(response)
    return response

@requiere_perfil(ROL_DIRECTOR_DAN)
def registrar_administrativo(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    if request.method == "POST":
        if 'archivo_excel' in request.FILES:
            archivo = request.FILES['archivo_excel']
            if not archivo.name.endswith('.xlsx'):
                messages.error(request, "Documento con formato no válido")
                return redirect("registrar_administrativo")
                
            resultado = servicio_administrativo_registrar_masivo_desde_excel(archivo, universidad_usuario)
            
            if resultado["error"]:
                messages.error(request, resultado["error"])
                return redirect("registrar_administrativo")
                
            for advertencia in resultado["advertencias"]:
                messages.warning(request, advertencia)
                
            if resultado["exitosos"] > 0:
                messages.success(request, f"{resultado['exitosos']} Administrativos registrados correctamente")
            else:
                messages.warning(request, "No se procesaron registros")
                
            return redirect("listar_administrativos")

        else:
            formulario_usuario = FormularioUsuarioDeSistema(request.POST)
            formulario_perfil = FormularioRegistrarPerfilAdministrativo(request.POST)

            if formulario_usuario.is_valid() and formulario_perfil.is_valid():
                with transaction.atomic():
                    usuario = formulario_usuario.save(commit=False)
                    usuario.set_password(usuario.identificacion)
                    usuario.save()

                    perfil = formulario_perfil.save(commit=False)
                    perfil.usuario_de_sistema = usuario
                    perfil.universidad = universidad_usuario

                    enum_perfil = EnumPerfilAdministrativo(perfil.perfil_administrativo)
                    prefijo = UsuarioAdministrativoBase.definir_prefijo_identificador(enum_perfil)

                    perfil.identificador_administrativo = generar_identificador_siguiente(
                        PerfilAdministrativo, prefijo, 'identificador_administrativo'
                    )

                    perfil.save()
                messages.success(request, "El Administrativo ha sido registrado correctamente")
                return redirect("listar_administrativos")
            
    else:
        formulario_usuario = FormularioUsuarioDeSistema()
        formulario_perfil = FormularioRegistrarPerfilAdministrativo()

    return render(request, "usuarios/formulario_administrativo.html", {
        "form_usuario": formulario_usuario,
        "form_perfil": formulario_perfil,
        "titulo": "Registrar Administrativo",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_administrativos",
        "mostrar_carga_masiva": True,
        "url_plantilla": "descargar_plantilla_administrativo"
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def modificar_administrativo(request, admin_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    perfil = get_object_or_404(PerfilAdministrativo, pk=admin_id, universidad=universidad_usuario)
    usuario = perfil.usuario_de_sistema
    
    admin_poo = _crear_usuario_administrativo(perfil)
    if not admin_poo.puede_ser_modificado_o_eliminado():
        messages.error(request, "El Administrativo no ha podido ser modificado")
        return redirect("listar_administrativos")

    perfil_docente = getattr(usuario, 'perfil_docente', None)
    es_coordinador_ua = perfil.perfil_administrativo == EnumPerfilAdministrativo.COORDINADOR_UA.value

    if request.method == "POST":
        formulario_usuario = FormularioModificarUsuarioDeSistema(request.POST, instance=usuario)
        if es_coordinador_ua:
            from usuarios.forms import FormularioModificarCoordinadorUA
            formulario_perfil = FormularioModificarCoordinadorUA(request.POST, instance=perfil, universidad=universidad_usuario)
        else:
            formulario_perfil = FormularioModificarPerfilAdministrativo(request.POST, instance=perfil)
        
        if es_coordinador_ua and perfil_docente:
            formulario_docente = FormularioDatosDocenteUA(request.POST, instance=perfil_docente)
            formularios_validos = formulario_usuario.is_valid() and formulario_perfil.is_valid() and formulario_docente.is_valid()
        else:
            formulario_docente = None
            formularios_validos = formulario_usuario.is_valid() and formulario_perfil.is_valid()

        if formularios_validos:
            with transaction.atomic():
                usuario_modificado = formulario_usuario.save(commit=False)
                nueva_contrasena = formulario_usuario.cleaned_data.get("contrasena")
                if nueva_contrasena:
                    usuario_modificado.set_password(nueva_contrasena)
                
                usuario_modificado.save()
                formulario_perfil.save()
                
                if formulario_docente:
                    docente_guardado = formulario_docente.save(commit=False)
                    docente_guardado.especialidades = formulario_docente.cleaned_data.get('especialidades', [])
                    docente_guardado.jornadas = formulario_docente.cleaned_data.get('jornadas', [])
                    docente_guardado.save()
            
            if es_coordinador_ua:
                messages.success(request, "El Coordinador de unidad académica ha sido modificado correctamente")
                return redirect("listar_coordinadores_ua")
            elif perfil.perfil_administrativo == EnumPerfilAdministrativo.COORDINADOR_DAN.value:
                messages.success(request, "El Coordinador de dirección de admisión y nivelación ha sido modificado correctamente")
                return redirect("listar_coordinadores_dan")
            else:
                messages.success(request, "El Administrativo ha sido modificado correctamente")
                return redirect("listar_administrativos")
    else:
        formulario_usuario = FormularioModificarUsuarioDeSistema(instance=usuario)
        if es_coordinador_ua:
            from usuarios.forms import FormularioModificarCoordinadorUA
            formulario_perfil = FormularioModificarCoordinadorUA(instance=perfil, universidad=universidad_usuario)
        else:
            formulario_perfil = FormularioModificarPerfilAdministrativo(instance=perfil)
        formulario_docente = FormularioDatosDocenteUA(instance=perfil_docente) if es_coordinador_ua and perfil_docente else None

    if es_coordinador_ua:
        url_cancelar = "listar_coordinadores_ua"
        titulo_pagina = "Coordinador de unidad académica - NIVEC"
        titulo_seccion = "Modificar Coordinador de unidad académica"
    elif perfil.perfil_administrativo == EnumPerfilAdministrativo.COORDINADOR_DAN.value:
        url_cancelar = "listar_coordinadores_dan"
        titulo_pagina = "Coordinador de dirección de admisión y nivelación - NIVEC"
        titulo_seccion = "Modificar Coordinador de dirección de admisión y nivelación"
    else:
        url_cancelar = "listar_administrativos"
        titulo_pagina = "Administrativo - NIVEC"
        titulo_seccion = "Modificar Administrativo"

    contexto = {
        "form_usuario": formulario_usuario,
        "form_perfil": formulario_perfil,
        "titulo": titulo_seccion,
        "subtitulo": f"{usuario.nombres} {usuario.apellidos}",
        "boton_texto": "Modificar",
        "url_cancelar": url_cancelar,
        "url_volver": url_cancelar,
        "titulo_pagina": titulo_pagina,
        "mostrar_carga_masiva": False
    }

    if formulario_docente:
        contexto["form_docente"] = formulario_docente

    return render(request, "usuarios/formulario_administrativo.html", contexto)

@requiere_perfil(ROL_DIRECTOR_DAN)
def eliminar_administrativo(request, admin_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    perfil = get_object_or_404(PerfilAdministrativo, pk=admin_id, universidad=universidad_usuario)
    
    admin_poo = _crear_usuario_administrativo(perfil)
    if not admin_poo.puede_ser_modificado_o_eliminado():
        messages.error(request, "El Administrativo no ha podido ser eliminado")
        return redirect("listar_administrativos")

    rol_eliminado = perfil.perfil_administrativo
    usuario = perfil.usuario_de_sistema
    usuario.delete()
    
    if rol_eliminado == EnumPerfilAdministrativo.COORDINADOR_DAN.value:
        messages.success(request, "El Coordinador de dirección de admisión y nivelación ha sido eliminado correctamente")
        return redirect("listar_coordinadores_dan")
    elif rol_eliminado == EnumPerfilAdministrativo.COORDINADOR_UA.value:
        messages.success(request, "El Coordinador de unidad académica ha sido eliminado correctamente")
        return redirect("listar_coordinadores_ua")
    else:
        messages.success(request, "El Usuario administrativo ha sido eliminado correctamente")
        return redirect("listar_administrativos")