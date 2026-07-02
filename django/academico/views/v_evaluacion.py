from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
import openpyxl

from academico.models import Paralelo, EvaluacionAcademica, PeriodoDeNivelacion, MatriculaParalelo, UnidadCurricular
from academico.services import servicio_cargar_calificaciones_desde_excel
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo
from usuarios.utils import (
    requiere_perfil, usuario_es_solo_lectura,
    ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR, ROL_COORDINADOR_UA, ROL_DOCENTE,
)

ROLES_CARGAR = (ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN, ROL_COORDINADOR_UA, ROL_DOCENTE)
ROLES_VER = (ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR, ROL_COORDINADOR_UA, ROL_DOCENTE)


def _obtener_universidad_usuario(user):
    """Get universidad from perfil_administrativo or perfil_docente."""
    perfil_admin = getattr(user, 'perfil_administrativo', None)
    if perfil_admin:
        return perfil_admin.universidad
    perfil_docente = getattr(user, 'perfil_docente', None)
    if perfil_docente:
        return perfil_docente.universidad
    return None


@requiere_perfil(*ROLES_VER)
def listar_evaluaciones_paralelo(request, paralelo_id):
    universidad_usuario = _obtener_universidad_usuario(request.user)
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )
    periodo = paralelo.periodo_de_nivelacion

    if periodo.estado not in (EstadoDePeriodo.EVALUACION.value, EstadoDePeriodo.CERRADO.value):
        messages.warning(request, "Las calificaciones solo están disponibles cuando el Periodo está en evaluación o cerrado")
        return redirect("detalle_paralelo", paralelo_id=paralelo.id)

    evaluaciones = EvaluacionAcademica.objects.filter(
        unidad_curricular=paralelo.unidad_curricular,
        periodo_de_nivelacion=periodo,
        estudiante__estudiantes_matriculados__paralelo=paralelo,
    ).select_related("estudiante__usuario_de_sistema").order_by(
        "estudiante__usuario_de_sistema__apellidos"
    )

    return render(request, "academico/evaluaciones_paralelo.html", {
        "paralelo": paralelo,
        "evaluaciones": evaluaciones,
        "periodo": periodo,
        "es_evaluacion": periodo.estado == EstadoDePeriodo.EVALUACION.value,
        "solo_lectura": usuario_es_solo_lectura(request.user),
        "titulo_pagina": "Calificaciones - NIVEC",
        "titulo": f"Calificaciones - {paralelo.nombre} ({paralelo.unidad_curricular.nombre})",
    })


@requiere_perfil(*ROLES_CARGAR)
def cargar_calificaciones(request, paralelo_id):
    universidad_usuario = _obtener_universidad_usuario(request.user)
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )
    periodo = paralelo.periodo_de_nivelacion

    if periodo.estado != EstadoDePeriodo.EVALUACION.value:
        messages.error(request, "Solo se pueden cargar calificaciones cuando el Periodo está en evaluación")
        return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)

    if request.method == "POST" and "archivo_excel" in request.FILES:
        archivo = request.FILES["archivo_excel"]
        if not archivo.name.endswith(".xlsx"):
            messages.error(request, "Documento con formato no válido")
            return redirect("cargar_calificaciones", paralelo_id=paralelo.id)

        resultado = servicio_cargar_calificaciones_desde_excel(
            archivo, paralelo, paralelo.unidad_curricular, periodo
        )

        if resultado["error"]:
            messages.error(request, resultado["error"])
        for adv in resultado["advertencias"]:
            messages.warning(request, adv)
        if resultado["exitosos"] > 0:
            messages.success(request, f"{resultado['exitosos']} calificaciones registradas correctamente")

        return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)

    return render(request, "academico/cargar_calificaciones.html", {
        "paralelo": paralelo,
        "titulo_pagina": "Calificaciones - NIVEC",
        "titulo": f"Cargar calificaciones - {paralelo.nombre} ({paralelo.unidad_curricular.nombre})",
    })


@requiere_perfil(*ROLES_CARGAR)
def descargar_plantilla_calificaciones(request, paralelo_id):
    universidad_usuario = _obtener_universidad_usuario(request.user)
    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Calificaciones"
    ws.append(["Número de identificación", "Apellidos", "Nombres", "Correo institucional", "Número de matrícula", "Parcial 1 (0-10)", "Parcial 2 (0-10)", "Porcentaje de asistencia (0-100)"])

    # Pre-fill with student data
    matriculas = MatriculaParalelo.objects.filter(
        paralelo=paralelo
    ).select_related("estudiante__usuario_de_sistema").order_by(
        "estudiante__usuario_de_sistema__apellidos"
    )
    for m in matriculas:
        ws.append([
            m.estudiante.usuario_de_sistema.identificacion,
            m.estudiante.usuario_de_sistema.apellidos,
            m.estudiante.usuario_de_sistema.nombres,
            m.estudiante.usuario_de_sistema.correo_institucional,
            m.estudiante.numero_de_matricula,
            "",
            "",
            "",
        ])

    for col in range(1, 9):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 30

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="calificaciones_{paralelo.nombre}_{paralelo.unidad_curricular.nombre}.xlsx"'.replace(" ", "_").lower()
    wb.save(response)
    return response


@requiere_perfil(*ROLES_VER)
def detalle_evaluacion(request, evaluacion_id):
    universidad_usuario = _obtener_universidad_usuario(request.user)
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    evaluacion = get_object_or_404(EvaluacionAcademica, id=evaluacion_id)
    unidad = evaluacion.unidad_curricular
    estudiante = evaluacion.estudiante
    usuario = estudiante.usuario_de_sistema

    # Métricas de aprobación definidas
    criterio_nota = unidad.criterio_de_aprobacion
    criterio_asistencia = unidad.porcentaje_minimo_asistencia

    # Métricas actuales del estudiante
    nota_actual = evaluacion.nota_final
    asistencia_actual = evaluacion.porcentaje_asistencia

    # Motivo detallado
    cumple_nota = nota_actual >= criterio_nota
    cumple_asistencia = asistencia_actual >= criterio_asistencia

    if evaluacion.estado_de_aprobacion == "Aprobado":
        motivo = "El estudiante cumple con el criterio mínimo de calificación y el porcentaje mínimo de asistencia."
    elif evaluacion.estado_de_aprobacion == "Retirado":
        motivo = "El estudiante se ha retirado del proceso de nivelación."
    elif evaluacion.estado_de_aprobacion == "Anulado":
        motivo = "La matrícula del estudiante ha sido anulada."
    else:
        razones = []
        if not cumple_nota:
            razones.append(f"La calificación final ({nota_actual}) no alcanza el criterio mínimo de aprobación ({criterio_nota})")
        if not cumple_asistencia:
            razones.append(f"El porcentaje de asistencia ({asistencia_actual}%) no alcanza el mínimo requerido ({criterio_asistencia}%)")
        motivo = ". ".join(razones) + "." if razones else "No cumple con los criterios de aprobación."

    return render(request, "academico/detalle_evaluacion.html", {
        "evaluacion": evaluacion,
        "estudiante": estudiante,
        "usuario": usuario,
        "unidad": unidad,
        "criterio_nota": criterio_nota,
        "criterio_asistencia": criterio_asistencia,
        "nota_actual": nota_actual,
        "asistencia_actual": asistencia_actual,
        "cumple_nota": cumple_nota,
        "cumple_asistencia": cumple_asistencia,
        "motivo": motivo,
        "titulo_pagina": "Evaluación - NIVEC",
        "titulo": f"Detalle de evaluación - {usuario.apellidos} {usuario.nombres}",
    })



@requiere_perfil(*ROLES_CARGAR)
def editar_evaluacion(request, evaluacion_id):
    universidad_usuario = _obtener_universidad_usuario(request.user)
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    evaluacion = get_object_or_404(EvaluacionAcademica, id=evaluacion_id)
    paralelo = Paralelo.objects.filter(
        unidad_curricular=evaluacion.unidad_curricular,
        periodo_de_nivelacion=evaluacion.periodo_de_nivelacion,
        estudiantes_matriculados__estudiante=evaluacion.estudiante,
    ).first()

    if not paralelo:
        messages.error(request, "No se encontró el paralelo asociado")
        return redirect("panel_principal")

    if evaluacion.estado_revision == "Formalizado":
        messages.error(request, "Las calificaciones formalizadas no se pueden editar")
        return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)

    periodo = evaluacion.periodo_de_nivelacion
    if periodo and periodo.estado != EstadoDePeriodo.EVALUACION.value:
        messages.error(request, "Solo se pueden editar calificaciones cuando el Periodo está en evaluación")
        return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)

    if request.method == "POST":
        try:
            p1 = float(request.POST.get("parcial_1", 0))
            p2 = float(request.POST.get("parcial_2", 0))
            asist = float(request.POST.get("asistencia", 0))
        except (ValueError, TypeError):
            messages.error(request, "Los valores ingresados no son válidos")
            return redirect("editar_evaluacion", evaluacion_id=evaluacion.id)

        if not (0 <= p1 <= 10) or not (0 <= p2 <= 10):
            messages.error(request, "Las calificaciones deben estar entre 0 y 10")
            return redirect("editar_evaluacion", evaluacion_id=evaluacion.id)
        if not (0 <= asist <= 100):
            messages.error(request, "La asistencia debe estar entre 0 y 100")
            return redirect("editar_evaluacion", evaluacion_id=evaluacion.id)

        unidad = evaluacion.unidad_curricular
        nota_final = round((p1 + p2) / 2, 2)
        
        if asist < unidad.porcentaje_minimo_asistencia:
            estado = "Reprobado"
        elif nota_final >= unidad.criterio_de_aprobacion:
            estado = "Aprobado"
        else:
            estado = "Reprobado"

        evaluacion.calificacion_parcial_1 = p1
        evaluacion.calificacion_parcial_2 = p2
        evaluacion.nota_final = nota_final
        evaluacion.porcentaje_asistencia = asist
        evaluacion.estado_de_aprobacion = estado
        evaluacion.save()

        messages.success(request, "La calificación ha sido actualizada correctamente")
        return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)

    return render(request, "academico/editar_evaluacion.html", {
        "evaluacion": evaluacion,
        "paralelo": paralelo,
        "titulo_pagina": "Editar calificación - NIVEC",
        "titulo": f"Editar calificación - {evaluacion.estudiante.usuario_de_sistema.apellidos} {evaluacion.estudiante.usuario_de_sistema.nombres}",
    })



@requiere_perfil(*ROLES_CARGAR)
def pasar_a_revision(request, paralelo_id):
    from academico.services import servicio_pasar_a_revision
    universidad_usuario = _obtener_universidad_usuario(request.user)
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )
    periodo = paralelo.periodo_de_nivelacion

    if periodo.estado != EstadoDePeriodo.EVALUACION.value:
        messages.error(request, "Solo se puede pasar a revisión cuando el Periodo está en evaluación")
        return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)

    if request.method != "POST":
        return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)

    # Check there are evaluations in Borrador
    from academico.models import EvaluacionAcademica as EA
    borradores = EA.objects.filter(
        unidad_curricular=paralelo.unidad_curricular,
        periodo_de_nivelacion=periodo,
        estado_revision="Borrador",
        estudiante__estudiantes_matriculados__paralelo=paralelo,
    ).count()

    if borradores == 0:
        messages.warning(request, "No existen calificaciones en borrador para pasar a revisión")
        return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)

    count = servicio_pasar_a_revision(paralelo)
    messages.success(request, f"{count} calificaciones pasadas a revisión correctamente")
    return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)


@requiere_perfil(*ROLES_CARGAR)
def formalizar_evaluaciones(request, paralelo_id):
    from academico.services import servicio_formalizar_evaluaciones
    universidad_usuario = _obtener_universidad_usuario(request.user)
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )
    periodo = paralelo.periodo_de_nivelacion

    if periodo.estado != EstadoDePeriodo.EVALUACION.value:
        messages.error(request, "Solo se puede formalizar cuando el Periodo está en evaluación")
        return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)

    if request.method != "POST":
        return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)

    from academico.models import EvaluacionAcademica as EA
    en_revision = EA.objects.filter(
        unidad_curricular=paralelo.unidad_curricular,
        periodo_de_nivelacion=periodo,
        estado_revision="En revisión",
        estudiante__estudiantes_matriculados__paralelo=paralelo,
    ).count()

    if en_revision == 0:
        messages.warning(request, "No existen calificaciones en revisión para formalizar")
        return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)

    count = servicio_formalizar_evaluaciones(paralelo)
    messages.success(request, f"{count} calificaciones formalizadas correctamente")
    return redirect("listar_evaluaciones_paralelo", paralelo_id=paralelo.id)
