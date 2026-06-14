from django.contrib import admin
from .models import Universidad
from .models import Campus
from .models import Carrera
from .models import MallaCurricular
from .models import UnidadCurricular
from .models import PeriodoDeNivelacion
from .models import Paralelo
from .models import Horario
from .models import CohorteDeMatricula
from .models import MatriculaParalelo
from .models import ConsolidadoAcademico
from .models import EvaluacionAcademica
from .models import IncidenciaAcademica
from .models import EvaluacionDeDesempeno
from .models import InformeGeneral


@admin.register(Universidad)
class UniversidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "abreviatura", "codigo_sniese")
    search_fields = ("nombre", "abreviatura", "codigo_sniese")
    ordering = ("nombre",)

    fieldsets = (
        (None, {
            "fields": (
                "nombre", 
                "abreviatura", 
                "codigo_sniese", 
                "direccion_matriz", 
                "identificador_visual"
            )
        }),
    )


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("nombre", "universidad", "provincia", "infraestructura_compartida")
    search_fields = ("nombre", "provincia", "codigo_de_campus")
    list_filter = ("infraestructura_compartida", "universidad")
    ordering = ("universidad", "nombre")

    fieldsets = (
        (None, {
            "fields": (
                "universidad", 
                "codigo_de_campus", 
                "nombre", 
                "direccion_fisica", 
                "provincia", 
                "infraestructura_compartida"
            )
        }),
    )


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ("nombre", "campus", "modalidad", "facultad", "vigencia_sniese")
    search_fields = ("nombre", "codigo_de_carrera", "facultad")
    list_filter = ("modalidad", "campus", "facultad")
    ordering = ("campus", "nombre")
    fieldsets = (
        (None, {
            "fields": (
                "campus", 
                "codigo_de_carrera", 
                "nombre", 
                "modalidad", 
                "facultad",
                "vigencia_sniese"
            )
        }),
    )


@admin.register(MallaCurricular)
class MallaCurricularAdmin(admin.ModelAdmin):
    list_display = ("nombre", "carrera", "version_de_malla", "modalidad", "estado", "total_horas_nivelacion")
    search_fields = ("nombre", "codigo_de_malla")
    list_filter = ("modalidad", "estado", "carrera")
    ordering = ("estado", "carrera", "nombre")

    fieldsets = (
        (None, {
            "fields": (
                "carrera", 
                "codigo_de_malla", 
                "nombre", 
                "area_de_conocimiento", 
                "duracion_semanas", 
                "version_de_malla", 
                "modalidad", 
                "estado", 
                "total_horas_nivelacion"
            )
        }),
    )


@admin.register(UnidadCurricular)
class UnidadCurricularAdmin(admin.ModelAdmin):
    list_display = ("codigo_de_unidad", "nombre", "malla_curricular", "tipo_de_componente", "horas_totales", "criterio_de_aprobacion", "porcentaje_minimo_asistencia")
    search_fields = ("codigo_de_unidad", "nombre")
    list_filter = ("tipo_de_componente", "malla_curricular")
    ordering = ("malla_curricular", "nombre")

    fieldsets = (
        (None, {
            "fields": (
                "malla_curricular", 
                "codigo_de_unidad", 
                "nombre", 
                "area_de_conocimiento", 
                "horas_totales", 
                "horas_semanales", 
                "horas_sincronicas", 
                "horas_asincronicas", 
                "tipo_de_componente", 
                "criterio_de_aprobacion", 
                "porcentaje_minimo_asistencia"
            )
        }),
    )


@admin.register(PeriodoDeNivelacion)
class PeriodoDeNivelacionAdmin(admin.ModelAdmin):
    list_display = ("periodo", "universidad", "anio", "numero_periodo", "modalidad", "fecha_inicio", "fecha_fin", "estado")
    search_fields = ("codigo_periodo", "periodo")
    list_filter = ("estado", "modalidad", "anio", "universidad")
    ordering = ("estado", "-anio", "numero_periodo")

    fieldsets = (
        (None, {
            "fields": (
                "universidad", 
                "codigo_periodo", 
                "anio", 
                "periodo", 
                "fecha_inicio", 
                "fecha_fin", 
                "modalidad", 
                "numero_periodo", 
                "estado"
            )
        }),
    )


@admin.register(Paralelo)
class ParaleloAdmin(admin.ModelAdmin):
    list_display = ("nombre", "periodo_de_nivelacion", "unidad_curricular", "docente_responsable", "jornada", "modalidad", "capacidad_maxima")
    search_fields = ("codigo_de_paralelo", "nombre")
    list_filter = ("jornada", "modalidad", "periodo_de_nivelacion")
    ordering = ("periodo_de_nivelacion", "unidad_curricular", "nombre")

    fieldsets = (
        (None, {
            "fields": (
                "periodo_de_nivelacion", 
                "unidad_curricular", 
                "codigo_de_paralelo", 
                "nombre", 
                "jornada", 
                "modalidad", 
                "capacidad_maxima", 
                "docente_responsable"
            )
        }),
    )


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("paralelo", "dia_semana", "hora_inicio", "hora_fin", "tipo_de_sesion", "espacio_de_imparticion", "numero_semana")
    search_fields = ("paralelo__nombre", "espacio_de_imparticion")
    list_filter = ("dia_semana", "tipo_de_sesion", "modalidad")
    ordering = ("paralelo", "dia_semana", "hora_inicio")

    fieldsets = (
        (None, {
            "fields": (
                "paralelo", 
                "dia_semana", 
                "hora_inicio", 
                "hora_fin", 
                "espacio_de_imparticion", 
                "modalidad", 
                "numero_semana", 
                "tipo_de_sesion"
            )
        }),
    )


@admin.register(CohorteDeMatricula)
class CohorteDeMatriculaAdmin(admin.ModelAdmin):
    list_display = ("codigo_de_registro", "nombre_cohorte", "periodo_de_nivelacion", "carrera_registrada", "tipo_de_cohorte", "estado_de_cohorte", "total_primera_matricula", "total_segunda_matricula", "total_exonerados", "fecha_de_cierre")
    search_fields = ("codigo_de_registro", "nombre_cohorte")
    list_filter = ("tipo_de_cohorte", "estado_de_cohorte", "periodo_de_nivelacion")
    ordering = ("estado_de_cohorte", "periodo_de_nivelacion", "nombre_cohorte")

    fieldsets = (
        (None, {
            "fields": (
                "periodo_de_nivelacion", 
                "carrera_registrada", 
                "codigo_de_registro", 
                "nombre_cohorte", 
                "fecha_de_cierre", 
                "tipo_de_cohorte", 
                "estado_de_cohorte", 
                "total_primera_matricula", 
                "total_segunda_matricula", 
                "total_exonerados"
            )
        }),
    )


@admin.register(MatriculaParalelo)
class MatriculaParaleloAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "paralelo", "cohorte_de_matricula", "fecha_registro")
    search_fields = ("estudiante__usuario_de_sistema__nombres", "estudiante__usuario_de_sistema__apellidos", "paralelo__nombre")
    list_filter = ("cohorte_de_matricula", "paralelo__periodo_de_nivelacion")
    ordering = ("cohorte_de_matricula", "paralelo", "estudiante__usuario_de_sistema__apellidos")
    
    readonly_fields = ("fecha_registro",)

    fieldsets = (
        (None, {
            "fields": (
                "estudiante", 
                "paralelo", 
                "cohorte_de_matricula", 
                "fecha_registro"
            )
        }),
    )


@admin.register(ConsolidadoAcademico)
class ConsolidadoAcademicoAdmin(admin.ModelAdmin):
    list_display = ("periodo_academico", "fecha_de_corte", "total_cupos_aceptados", "registros_totales", "registros_validos", "registros_observados")
    search_fields = ("periodo_academico__periodo",)
    ordering = ("-fecha_de_corte",)

    fieldsets = (
        (None, {
            "fields": (
                "periodo_academico", 
                "fecha_de_corte", 
                "total_cupos_aceptados", 
                "registros_totales", 
                "registros_validos", 
                "registros_observados"
            )
        }),
    )


@admin.register(EvaluacionAcademica)
class EvaluacionAcademicaAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "unidad_curricular", "calificacion_parcial_1", "calificacion_parcial_2", "nota_final", "porcentaje_asistencia", "estado_de_aprobacion")
    search_fields = ("estudiante__usuario_de_sistema__nombres", "estudiante__usuario_de_sistema__apellidos", "unidad_curricular__nombre")
    list_filter = ("estado_de_aprobacion", "unidad_curricular")
    ordering = ("estado_de_aprobacion", "estudiante__usuario_de_sistema__apellidos", "estudiante__usuario_de_sistema__nombres")

    fieldsets = (
        (None, {
            "fields": (
                "estudiante", 
                "unidad_curricular", 
                "calificacion_parcial_1", 
                "calificacion_parcial_2", 
                "nota_final", 
                "porcentaje_asistencia", 
                "estado_de_aprobacion", 
                "observacion"
            )
        }),
    )


@admin.register(IncidenciaAcademica)
class IncidenciaAcademicaAdmin(admin.ModelAdmin):
    list_display = ("codigo_incidencia", "docente_implicado", "fecha_incidencia", "responsable_autorizacion")
    search_fields = ("codigo_incidencia", "docente_implicado__usuario_de_sistema__nombres", "docente_implicado__usuario_de_sistema__apellidos")
    list_filter = ("fecha_incidencia",)
    ordering = ("-fecha_incidencia",)

    fieldsets = (
        (None, {
            "fields": (
                "codigo_incidencia", 
                "docente_implicado", 
                "descripcion", 
                "fecha_incidencia", 
                "responsable_autorizacion"
            )
        }),
    )


@admin.register(EvaluacionDeDesempeno)
class EvaluacionDeDesempenoAdmin(admin.ModelAdmin):
    list_display = ("docente_responsable", "periodo_de_nivelacion", "porcentaje_de_horas_cumplidas", "entrega_oportuna_de_calificaciones", "porcentaje_de_aprobacion_paralelo", "resultado_de_evaluacion_estudiantil", "puntaje_final")
    search_fields = ("docente_responsable__usuario_de_sistema__nombres", "docente_responsable__usuario_de_sistema__apellidos")
    list_filter = ("periodo_de_nivelacion", "entrega_oportuna_de_calificaciones")
    ordering = ("periodo_de_nivelacion", "docente_responsable__usuario_de_sistema__apellidos")

    fieldsets = (
        (None, {
            "fields": (
                "periodo_de_nivelacion",
                "docente_responsable",  
                "porcentaje_de_horas_cumplidas", 
                "entrega_oportuna_de_calificaciones", 
                "porcentaje_de_aprobacion_paralelo", 
                "resultado_de_evaluacion_estudiantil", 
                "puntaje_final"
            )
        }),
    )


@admin.register(InformeGeneral)
class InformeGeneralAdmin(admin.ModelAdmin):
    list_display = ("codigo_de_informe", "periodo_academico", "tipo_de_informe", "estado_de_informe", "fecha_de_emision")
    search_fields = ("codigo_de_informe",)
    list_filter = ("tipo_de_informe", "estado_de_informe", "periodo_academico")
    ordering = ("estado_de_informe", "-fecha_de_emision")
    
    filter_horizontal = ("cohortes",)

    fieldsets = (
        (None, {
            "fields": (
                "periodo_academico", 
                "codigo_de_informe", 
                "tipo_de_informe", 
                "estado_de_informe", 
                "fecha_de_emision", 
                "cohortes"
            )
        }),
    )