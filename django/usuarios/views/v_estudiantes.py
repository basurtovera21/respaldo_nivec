from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import openpyxl

from usuarios.models import UsuarioDeSistema, PerfilEstudiante
from usuarios.forms import FormularioUsuarioDeSistema, FormularioModificarUsuarioDeSistema, FormularioPerfilEstudiante
from usuarios.utils import (
    generar_identificador_siguiente, requiere_perfil, usuario_es_solo_lectura,
    ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN, ROL_RECTOR, ROL_VICERRECTOR,
)

from usuarios.services import servicio_estudiante_registrar_masivo_desde_excel, _crear_estudiante

from poo.clases.enums.estado_de_usuario import EstadoDeUsuario as EnumEstadoDeUsuario
from poo.clases.enums.estado_de_matricula import EstadoDeMatricula as EnumEstadoDeMatricula
from poo.clases.servicios.centro_de_operacion_academica import CentroDeOperacionAcademica
from academico.models import PeriodoDeNivelacion

ROLES_USUARIOS_VEN = (ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN, ROL_RECTOR, ROL_VICERRECTOR)

@requiere_perfil(*ROLES_USUARIOS_VEN)
def listar_estudiantes(request):
    universidad_usuario = request.user.perfil_administrativo.universidad

    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    periodos = PeriodoDeNivelacion.objects.filter(
        universidad=universidad_usuario
    ).order_by("-anio", "-numero_periodo")

    periodo_id = request.GET.get("periodo") or None
    periodo_seleccionado = periodos.filter(id=periodo_id).first() if periodo_id else None

    estudiantes = PerfilEstudiante.objects.filter(
        carrera_registrada__campus__universidad=universidad_usuario
    )
    if periodo_seleccionado:
        estudiantes = estudiantes.filter(periodo_de_nivelacion=periodo_seleccionado)

    busqueda = request.GET.get("busqueda", "").strip()
    if busqueda:
        from django.db.models import Q
        estudiantes = estudiantes.filter(
            Q(usuario_de_sistema__nombres__icontains=busqueda) |
            Q(usuario_de_sistema__apellidos__icontains=busqueda)
        )

    from academico.models import Campus, Carrera
    campus_disponibles = Campus.objects.filter(universidad=universidad_usuario).order_by("nombre")
    carreras_disponibles = Carrera.objects.filter(campus__universidad=universidad_usuario).order_by("nombre")

    campus_filtro = request.GET.get("campus", "")
    if campus_filtro:
        estudiantes = estudiantes.filter(campus_registrado_id=campus_filtro)

    carrera_filtro = request.GET.get("carrera", "")
    if carrera_filtro:
        estudiantes = estudiantes.filter(carrera_registrada_id=carrera_filtro)

    estudiantes = estudiantes.select_related("usuario_de_sistema", "carrera_registrada", "campus_registrado").order_by("identificador_institucional")

    return render(request, "usuarios/listar_estudiantes.html", {
        "estudiantes": estudiantes,
        "busqueda": busqueda,
        "periodos": periodos,
        "periodo_seleccionado": periodo_seleccionado,
        "campus_disponibles": campus_disponibles,
        "carreras_disponibles": carreras_disponibles,
        "campus_filtro": campus_filtro,
        "carrera_filtro": carrera_filtro,
        "titulo_pagina": "Estudiante - NIVEC",
        "titulo": "Estudiantes",
        "url_registrar": "registrar_estudiante",
        "texto_registrar": "Registrar",
        "url_volver": "panel_principal",
        "solo_lectura": usuario_es_solo_lectura(request.user),
    })

@requiere_perfil(ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN)
def descargar_plantilla_estudiante(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Estudiantes"
    
    cabeceras = [
        "Tipo de identificación (Cédula, Pasaporte, Cédula extranjera)", 
        "Número de identificación", "Nombres", "Apellidos", "Correo institucional",
        "Código de Periodo (PNV...)",
        "Código de Carrera (CAR..)",
        "Jornada registrada (Matutina, Vespertina, Nocturna)", 
        "Registro de cupo (Registro regular, Segunda matrícula, Proceso de exoneración)"
    ]
    ws.append(cabeceras)
    
    for col in range(1, len(cabeceras) + 1): 
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 40
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="estudiante_documento_nivec.xlsx"'
    wb.save(response)
    return response

@requiere_perfil(ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN)
def registrar_estudiante(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")
    
    if not PeriodoDeNivelacion.objects.filter(universidad=universidad_usuario).exists():
        messages.warning(request, "No existen registros de Periodos de nivelación actualmente")
        return redirect("panel_principal")

    # El periodo se toma del contexto (filtro del listado): GET al entrar, campo oculto al enviar.
    periodo_id = request.POST.get("periodo") or request.GET.get("periodo") or None
    periodos = PeriodoDeNivelacion.objects.filter(
        universidad=universidad_usuario
    ).order_by("-anio", "-numero_periodo")
    periodo = periodos.filter(id=periodo_id).first() if periodo_id else None
    if not periodo:
        # Respaldo: si no llegó un periodo, usa el más reciente (nunca reinicia).
        periodo = periodos.first()

    url_registrar = f"{reverse('registrar_estudiante')}?periodo={periodo.id}"
    url_listar = f"{reverse('listar_estudiantes')}?periodo={periodo.id}"

    if request.method == "POST":
        if 'archivo_excel' in request.FILES:
            archivo = request.FILES['archivo_excel']
            if not archivo.name.endswith('.xlsx'):
                messages.error(request, "Documento con formato no válido")
                return redirect(url_registrar)

            resultado = servicio_estudiante_registrar_masivo_desde_excel(
                archivo, universidad_usuario, periodo_de_nivelacion=periodo
            )

            if resultado["error"]: messages.error(request, resultado["error"])
            for adv in resultado["advertencias"]: messages.warning(request, adv)
            if resultado["exitosos"] > 0: messages.success(request, f"{resultado['exitosos']} Estudiantes registrados correctamente")
            return redirect(url_listar)
                
        else:
            formulario_usuario = FormularioUsuarioDeSistema(request.POST)
            formulario_estudiante = FormularioPerfilEstudiante(request.POST, universidad=universidad_usuario)

            if formulario_usuario.is_valid() and formulario_estudiante.is_valid():
                with transaction.atomic():
                    usuario = formulario_usuario.save(commit=False)
                    usuario.estado_de_usuario = "Activo"
                    usuario.set_password(usuario.identificacion)
                    usuario.save()
                    
                    estudiante = formulario_estudiante.save(commit=False)
                    estudiante.usuario_de_sistema = usuario
                    estudiante.identificador_institucional = generar_identificador_siguiente(PerfilEstudiante, "ES", 'identificador_institucional')
                    estudiante.numero_de_matricula = generar_identificador_siguiente(PerfilEstudiante, "MAT", 'numero_de_matricula')
                    estudiante.estado_de_matricula = EnumEstadoDeMatricula.MATRICULADO.value
                    estudiante.campus_registrado = estudiante.carrera_registrada.campus
                    estudiante.save()
                
                messages.success(request, "El Estudiante ha sido registrado correctamente")
                return redirect(url_listar)
    else:
        formulario_usuario = FormularioUsuarioDeSistema()
        formulario_estudiante = FormularioPerfilEstudiante(universidad=universidad_usuario)

    formulario_usuario.fields.pop('estado_de_usuario', None)
    return render(request, "usuarios/formulario_estudiante.html", {
        "form_usuario": formulario_usuario,
        "form_estudiante": formulario_estudiante,
        "periodo_contexto": periodo,
        "titulo_pagina": "Estudiante - NIVEC",
        "titulo": "Registrar Estudiante",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_estudiantes",
        "mostrar_carga_masiva": True,
        "url_plantilla": "descargar_plantilla_estudiante"
    })

@requiere_perfil(ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN)
def modificar_estudiante(request, estudiante_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")
    
    if not PeriodoDeNivelacion.objects.filter(universidad=universidad_usuario).exists():
        messages.warning(request, "No existen registros de Periodos de nivelación actualmente")
        return redirect("panel_principal")

    est = get_object_or_404(PerfilEstudiante, id=estudiante_id, carrera_registrada__campus__universidad=universidad_usuario)
    usuario = est.usuario_de_sistema
    
    if request.method == "POST":
        form_u = FormularioModificarUsuarioDeSistema(request.POST, instance=usuario)
        form_e = FormularioPerfilEstudiante(request.POST, instance=est, universidad=universidad_usuario)

        if form_u.is_valid() and form_e.is_valid():
            with transaction.atomic():
                user_saved = form_u.save(commit=False)
                nueva_contrasena = form_u.cleaned_data.get('contrasena')
                if nueva_contrasena:
                    user_saved.set_password(nueva_contrasena)
                user_saved.save()
                estudiante = form_e.save(commit=False)
                estudiante.campus_registrado = estudiante.carrera_registrada.campus
                estudiante.save()
            
            messages.success(request, "El Estudiante ha sido modificado correctamente")
            return redirect("listar_estudiantes")
    else:
        form_u = FormularioModificarUsuarioDeSistema(instance=usuario)
        form_e = FormularioPerfilEstudiante(instance=est, universidad=universidad_usuario)
        
    form_u.fields.pop('estado_de_usuario', None)
    return render(request, "usuarios/formulario_estudiante.html", {
        "form_usuario": form_u, 
        "form_estudiante": form_e, 
        "titulo": "Modificar Estudiante",
        "subtitulo": f"{usuario.nombres} {usuario.apellidos}",
        "boton_texto": "Modificar",
        "url_cancelar": "listar_estudiantes",
        "url_volver": "listar_estudiantes",
        "titulo_pagina": "Estudiante - NIVEC",
        "mostrar_carga_masiva": False
    })

@requiere_perfil(ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN)
def eliminar_estudiante(request, estudiante_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    estudiante = get_object_or_404(PerfilEstudiante, id=estudiante_id, carrera_registrada__campus__universidad=universidad_usuario)
    
    with transaction.atomic():
        estudiante.usuario_de_sistema.delete()
    
    messages.success(request, "El Estudiante ha sido eliminado correctamente")
    return redirect("listar_estudiantes")

@requiere_perfil(ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN)
def formalizar_matricula(request, estudiante_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    est_db = get_object_or_404(PerfilEstudiante, id=estudiante_id, carrera_registrada__campus__universidad=universidad_usuario)

    est_poo = _crear_estudiante(est_db)
    CentroDeOperacionAcademica().formalizar_matricula(est_poo)
    with transaction.atomic():
        est_db.estado_de_matricula = est_poo._estado_de_matricula.value
        est_db.save()
        # Restore access
        usuario = est_db.usuario_de_sistema
        usuario.estado_de_usuario = "Activo"
        usuario.is_active = True
        usuario.save()
        
    messages.success(request, "La matrícula del Estudiante ha sido reincorporada correctamente")
    return redirect("listar_estudiantes")

@requiere_perfil(ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN)
def anular_matricula(request, estudiante_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    est_db = get_object_or_404(
        PerfilEstudiante, id=estudiante_id,
        carrera_registrada__campus__universidad=universidad_usuario
    )

    est_poo = _crear_estudiante(est_db)
    CentroDeOperacionAcademica().anular_matricula(est_poo)
    
    with transaction.atomic():
        est_db.estado_de_matricula = est_poo._estado_de_matricula.value
        est_db.save()
        # Block access
        usuario = est_db.usuario_de_sistema
        usuario.estado_de_usuario = "Bloqueado"
        usuario.is_active = False
        usuario.save()
        # Set evaluaciones to Anulado
        from academico.models import EvaluacionAcademica
        EvaluacionAcademica.objects.filter(
            estudiante=est_db, estado_de_aprobacion="Pendiente"
        ).update(estado_de_aprobacion="Anulado", observacion="Anulación de matrícula")
        
    messages.success(request, "La matrícula del Estudiante ha sido anulada correctamente")
    return redirect("listar_estudiantes")

@requiere_perfil(ROL_DIRECTOR_DAN, ROL_COORDINADOR_DAN)
def solicitar_retiro(request, estudiante_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    est_db = get_object_or_404(
        PerfilEstudiante, id=estudiante_id,
        carrera_registrada__campus__universidad=universidad_usuario
    )
    
    est_poo = _crear_estudiante(est_db)
    if CentroDeOperacionAcademica().solicitar_retiro(est_poo):
        with transaction.atomic():
            est_db.estado_de_matricula = est_poo._estado_de_matricula.value
            est_db.save()
            # Block access
            usuario = est_db.usuario_de_sistema
            usuario.estado_de_usuario = "Bloqueado"
            usuario.is_active = False
            usuario.save()
            # Set evaluaciones to Retirado
            from academico.models import EvaluacionAcademica
            EvaluacionAcademica.objects.filter(
                estudiante=est_db, estado_de_aprobacion="Pendiente"
            ).update(estado_de_aprobacion="Retirado", observacion="Retiro académico")
        messages.success(request, "El retiro del Estudiante ha sido procesado correctamente")
    else:
        messages.warning(request, "No se ha podido procesar el retiro")
    return redirect("listar_estudiantes")