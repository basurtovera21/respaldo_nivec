"""
Módulo centralizado de permisos basados en el estado del Periodo de Nivelación.

Determina qué acciones están permitidas en cada módulo según el estado
del periodo activo (o la ausencia de uno).

Estados posibles:
    - SIN_PERIODO: No existe ningún periodo registrado
    - PLANIFICACION: Periodo en planificación
    - EN_CURSO: Periodo iniciado (en curso)
    - EVALUACION: Periodo en fase de evaluación
    - CERRADO: Periodo finalizado

Uso desde vistas:
    from academico.permisos import obtener_permisos_periodo
    permisos = obtener_permisos_periodo(universidad)
    # permisos["puede_modificar_universidad"] → True/False
"""

from academico.models import PeriodoDeNivelacion
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo


def _obtener_estado_periodo_activo(universidad):
    """
    Determina el estado del periodo más relevante (no cerrado).
    Prioridad: EN_CURSO > EVALUACION > PLANIFICACION.
    Si solo hay cerrados o no hay periodos → "SIN_PERIODO_ACTIVO".
    """
    if not universidad:
        return "SIN_PERIODO"

    periodos = PeriodoDeNivelacion.objects.filter(universidad=universidad)

    if not periodos.exists():
        return "SIN_PERIODO"

    # Buscar en orden de prioridad
    if periodos.filter(estado=EstadoDePeriodo.EN_CURSO.value).exists():
        return "EN_CURSO"
    if periodos.filter(estado=EstadoDePeriodo.EVALUACION.value).exists():
        return "EVALUACION"
    if periodos.filter(estado=EstadoDePeriodo.PLANIFICACION.value).exists():
        return "PLANIFICACION"

    # Solo hay periodos cerrados → se puede crear uno nuevo (equivale a sin periodo activo)
    return "SOLO_CERRADOS"


def obtener_permisos_periodo(universidad):
    """
    Retorna un diccionario con todos los permisos del sistema basados
    en el estado del periodo de nivelación.

    Returns:
        dict con claves booleanas para cada permiso
    """
    estado = _obtener_estado_periodo_activo(universidad)

    es_editable = estado in ("SIN_PERIODO", "PLANIFICACION", "SOLO_CERRADOS")

    es_gestionable = estado in ("SIN_PERIODO", "PLANIFICACION", "EN_CURSO", "SOLO_CERRADOS")

    es_planificacion = estado == "PLANIFICACION"

    es_en_curso = estado == "EN_CURSO"

    es_evaluacion = estado == "EVALUACION"

    es_cerrado = estado == "CERRADO"

    es_planificacion_o_en_curso = estado in ("PLANIFICACION", "EN_CURSO")

    return {
        "estado_periodo": estado,

        # ── UNIVERSIDAD ──
        "puede_modificar_universidad": es_editable,

        # ── CAMPUS ──
        "puede_registrar_campus": es_editable,
        "puede_modificar_campus": es_editable,
        "puede_eliminar_campus": es_editable,

        # ── CARRERAS ──
        "puede_registrar_carrera": es_editable,
        "puede_modificar_carrera": es_editable,
        "puede_eliminar_carrera": es_editable,

        # ── PERIODOS ──
        "puede_registrar_periodo": estado in ("SIN_PERIODO", "PLANIFICACION", "SOLO_CERRADOS"),
        "puede_modificar_periodo": es_planificacion,
        "puede_eliminar_periodo": es_planificacion,
        "puede_iniciar_periodo": es_planificacion,
        "puede_pasar_a_evaluacion": es_en_curso,
        "puede_finalizar_periodo": es_evaluacion,

        # ── ADMINISTRATIVOS / COORDINADORES ──
        "puede_registrar_administrativo": es_gestionable,
        "puede_modificar_administrativo": es_gestionable,
        "puede_eliminar_administrativo": es_gestionable,

        # ── DOCENTES ──
        "puede_registrar_docente": es_editable,
        "puede_modificar_docente": es_gestionable,
        "puede_eliminar_docente": es_editable,
        "puede_inhabilitar_docente": es_gestionable,

        # ── ESTUDIANTES ──
        "puede_registrar_estudiante": es_editable,
        "puede_modificar_estudiante": es_planificacion_o_en_curso,
        "puede_eliminar_estudiante": es_editable,
        "puede_matricular_estudiante": es_planificacion_o_en_curso,
        "puede_retirar_estudiante": estado in ("PLANIFICACION", "EN_CURSO", "EVALUACION"),
        "puede_anular_estudiante": estado in ("PLANIFICACION", "EN_CURSO", "EVALUACION"),
        "puede_reincorporar_estudiante": es_planificacion_o_en_curso,

        # ── MALLAS CURRICULARES ──
        "puede_registrar_malla": es_editable,
        "puede_modificar_malla": es_editable,
        "puede_eliminar_malla": es_editable,
        "puede_copiar_malla": es_editable,
        "puede_cambiar_estado_malla": es_editable,

        # ── UNIDADES CURRICULARES ──
        "puede_registrar_unidad": es_editable,
        "puede_modificar_unidad": es_editable,
        "puede_eliminar_unidad": es_editable,

        # ── MTN ──
        "puede_procesar_mtn": es_planificacion,

        # ── PARALELOS ──
        "puede_distribuir_paralelos": es_planificacion,
        "puede_eliminar_paralelo": es_planificacion,

        # ── DESIGNACIÓN DOCENTE ──
        "puede_designar_docente": es_planificacion_o_en_curso,

        # ── HORARIOS ──
        "puede_configurar_horario": es_planificacion,
        "puede_editar_horario": es_planificacion,
        "puede_eliminar_horario": es_planificacion,

        # ── ESTUDIANTES EN PARALELO ──
        "puede_reasignar_estudiante_paralelo": es_planificacion_o_en_curso,
        "puede_incorporar_estudiante_paralelo": es_planificacion_o_en_curso,

        # ── CALIFICACIONES ──
        "puede_gestionar_calificaciones": es_evaluacion,

        # ── INFORMES ──
        "puede_generar_informe": estado in ("EVALUACION", "SOLO_CERRADOS"),

        # ── VISUALIZACIÓN (siempre que haya registros) ──
        "puede_ver_matriz_horarios": True,
        "puede_ver_paralelos": True,
        "puede_ver_calificaciones": estado in ("EVALUACION", "SOLO_CERRADOS"),
    }



def todas_calificaciones_formalizadas_por_carrera(universidad, carrera=None):
    """
    Verifica si todas las evaluaciones académicas del periodo activo están formalizadas.
    Si se especifica carrera, verifica solo para esa carrera.
    
    Returns: True si todas están formalizadas (o no hay evaluaciones), False si hay pendientes.
    """
    from academico.models import EvaluacionAcademica, PeriodoDeNivelacion
    
    if not universidad:
        return False
    
    # Obtener periodo activo en evaluación o cerrado
    periodo = PeriodoDeNivelacion.objects.filter(
        universidad=universidad,
        estado__in=[EstadoDePeriodo.EVALUACION.value, EstadoDePeriodo.CERRADO.value]
    ).first()
    
    if not periodo:
        return False
    
    evaluaciones = EvaluacionAcademica.objects.filter(periodo_de_nivelacion=periodo)
    
    if carrera:
        evaluaciones = evaluaciones.filter(
            estudiante__carrera_registrada=carrera
        )
    
    if not evaluaciones.exists():
        return False
    
    # Verificar si alguna NO está formalizada
    no_formalizadas = evaluaciones.exclude(estado_revision="Formalizado").exists()
    return not no_formalizadas
