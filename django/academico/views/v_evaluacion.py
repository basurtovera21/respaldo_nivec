from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
import openpyxl

from academico.models import Paralelo, EvaluacionAcademica, PeriodoDeNivelacion, MatriculaParalelo, UnidadCurricular
from academico.services import servicio_cargar_calificaciones_desde_excel
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo
from usuarios.utils import (
    requiere_perfil, usuario_es_solo_lectura,
    ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR,
)

# Coordinador UA and Docente will access these too (add their roles later)
ROLES_CARGAR = (ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN)
ROLES_VER = (ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR)


@requiere_perfil(*ROLES_VER)
def listar_evaluaciones_paralelo(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
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
    universidad_usuario = request.user.perfil_administrativo.universidad
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
    universidad_usuario = request.user.perfil_administrativo.universidad
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
    universidad_usuario = request.user.perfil_administrativo.universidad
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
