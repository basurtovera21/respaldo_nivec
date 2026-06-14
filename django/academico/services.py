import openpyxl
from datetime import date

from poo.clases.enums.estado_de_matricula import EstadoDeMatricula
from poo.clases.enums.estado_de_aprobacion import EstadoDeAprobacion
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo
from poo.clases.enums.formato_de_exportacion import FormatoDeExportacion
from poo.clases.enums.modalidad import Modalidad
from poo.clases.enums.jornada import Jornada
from poo.clases.enums.tipo_de_cohorte import TipoDeCohorte
from poo.clases.enums.tipo_de_componente import TipoDeComponente
from poo.clases.enums.dia_de_semana import DiaDeSemana
from poo.clases.enums.tipo_de_sesion import TipoDeSesion

from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion as PeriodoDeNivelacionBase
from poo.clases.evaluacion_academica import EvaluacionAcademica as EvaluacionAcademica
from poo.clases.informe_general import InformeGeneral as InformeGeneralPOO
from poo.clases.servicios.procesador_de_informe import ProcesadorDeInforme
from poo.clases.cohorte_de_matricula import CohorteDeMatricula as CohorteDeMatriculaPOO
from poo.clases.horario import Horario as HorarioPOO
from poo.clases.servicios.distribuidor_de_estudiantes import DistribuidorDeEstudiantes
from poo.clases.consolidado_academico import ConsolidadoAcademico as ConsolidadoAcademicoPOO

from django.http import HttpResponse
from .models import (PeriodoDeNivelacion, Paralelo, EvaluacionAcademica, CohorteDeMatricula, InformeGeneral, ConsolidadoAcademico, MatriculaParalelo, Horario, MallaCurricular)
from usuarios.models import PerfilEstudiante


#PeriodoDeNivelacion
#Constructor
def _construir_periodo_de_nivelacion(periodo_de_nivelacion: PeriodoDeNivelacion):
    return PeriodoDeNivelacionBase(
        codigo_periodo = periodo_de_nivelacion.codigo_periodo,
        anio = periodo_de_nivelacion.anio,
        periodo = periodo_de_nivelacion.periodo,
        fecha_inicio = periodo_de_nivelacion.fecha_inicio,
        fecha_fin = periodo_de_nivelacion.fecha_fin,
        modalidad = Modalidad(periodo_de_nivelacion.modalidad),
        numero_periodo = periodo_de_nivelacion.numero_periodo,
        estado = EstadoDePeriodo(periodo_de_nivelacion.estado)
    )
    
def servicio_iniciar_periodo_de_nivelacion(periodo_de_nivelacion: PeriodoDeNivelacion):
    periodo = _construir_periodo_de_nivelacion(periodo_de_nivelacion)
    puede_iniciar = periodo.iniciar_periodo_de_nivelacion()
    if puede_iniciar:
        periodo_de_nivelacion.estado = EstadoDePeriodo.EN_CURSO.value
        periodo_de_nivelacion.save()
    return puede_iniciar

def servicio_finalizar_periodo_de_nivelacion(periodo_de_nivelacion: PeriodoDeNivelacion):
    periodo = _construir_periodo_de_nivelacion(periodo_de_nivelacion)
    puede_finalizar = periodo.finalizar_periodo_de_nivelacion()
    if puede_finalizar:
        periodo_de_nivelacion.estado = EstadoDePeriodo.CERRADO.value
        periodo_de_nivelacion.save()
    return puede_finalizar


def servicio_registrar_evaluacion_academica(evaluacion_academica: EvaluacionAcademica):
    from poo.clases.unidad_curricular import UnidadCurricular as UnidadCurricularBase
    from usuarios.services import _construir_estudiante

    unidad_curricular_base = UnidadCurricularBase(
        codigo_de_unidad = evaluacion_academica.unidad_curricular.codigo_de_unidad,
        nombre = evaluacion_academica.unidad_curricular.nombre,
        area_de_conocimiento = evaluacion_academica.unidad_curricular.area_de_conocimiento,
        horas_totales = evaluacion_academica.unidad_curricular.horas_totales,
        horas_semanales = evaluacion_academica.unidad_curricular.horas_semanales,
        horas_sincronicas = evaluacion_academica.unidad_curricular.horas_sincronicas,
        horas_asincronicas = evaluacion_academica.unidad_curricular.horas_asincronicas,
        tipo_de_componente = TipoDeComponente(evaluacion_academica.unidad_curricular.tipo_de_componente),
        criterio_de_aprobacion = evaluacion_academica.unidad_curricular.criterio_de_aprobacion,
        porcentaje_minimo_asistencia = evaluacion_academica.unidad_curricular.porcentaje_minimo_asistencia
    )
    estudiante = _construir_estudiante(evaluacion_academica.estudiante)
    evaluacion = EvaluacionAcademica(estudiante = estudiante, unidad_curricular = unidad_curricular_base)
    
    evaluacion.registrar_calificacion(1, evaluacion_academica.calificacion_parcial_1)
    evaluacion.registrar_calificacion(2, evaluacion_academica.calificacion_parcial_2)
    evaluacion.registrar_asistencia_final(evaluacion_academica.porcentaje_asistencia)
    nota_final = evaluacion.calcular_nota_final()
    estado = evaluacion.verificar_aprobacion()

    evaluacion_academica.nota_final = nota_final
    evaluacion_academica.estado_de_aprobacion = estado.value
    evaluacion_academica.observacion = evaluacion._observacion
    evaluacion_academica.save()


def servicio_distribuir_estudiantes(periodo_de_nivelacion: PeriodoDeNivelacion):
    paralelos = Paralelo.objects.filter(periodo_de_nivelacion_base=periodo_de_nivelacion)
    aspirantes = PerfilEstudiante.objects.filter(
        estado_de_matricula = EstadoDeMatricula.ASPIRANTE.value,
        carrera_registrada__campus__universidad = periodo_de_nivelacion.universidad
    )

    from usuarios.services import _construir_estudiante
    from poo.clases.paralelo import Paralelo as ParaleloBase
    from poo.clases.enums.jornada import Jornada

    paralelos_base = []
    indice_paralelo = {}

    for paralelo in paralelos:
        paralelo_base = ParaleloBase(
            codigo_de_paralelo = paralelo.codigo_de_paralelo,
            nombre = paralelo.nombre,
            jornada = Jornada(paralelo.jornada),
            modalidad = Modalidad(paralelo.modalidad),
            capacidad_maxima = paralelo.capacidad_maxima
        )
        paralelos_base.append(paralelo_base)
        indice_paralelo[paralelo.codigo_de_paralelo] = paralelo

    estudiantes_base = []
    indice_estudiante = {}

    for aspirante in aspirantes:
        estudiante_base = _construir_estudiante(aspirante)
        estudiantes_base.append(estudiante_base)
        indice_estudiante[aspirante.identificador_institucional] = aspirante

    distribuidor_de_estudiantes = DistribuidorDeEstudiantes(paralelos_base)
    estudiantes_no_asignados_base = distribuidor_de_estudiantes.distribuir(estudiantes_base)

    for paralelo_base in paralelos_base:
        paralelo = indice_paralelo[paralelo_base.codigo_de_paralelo]
        for estudiante_base in paralelo_base._estudiantes_matriculados:
            perfil_estudiante = indice_estudiante.get(estudiante_base.identificador_institucional)
            if perfil_estudiante:
                if not MatriculaParalelo.objects.filter(estudiante=perfil_estudiante, paralelo=paralelo).exists():
                    MatriculaParalelo.objects.create(
                        estudiante = perfil_estudiante,
                        paralelo = paralelo,
                        cohorte_de_matricula = CohorteDeMatricula.objects.filter(
                            periodo_de_nivelacion = periodo_de_nivelacion,
                            carrera_registrada = perfil_estudiante.carrera_registrada
                        ).first()
                    )
                perfil_estudiante.estado_de_matricula = EstadoDeMatricula.MATRICULADO.value
                perfil_estudiante.save()

    return [indice_estudiante[e.identificador_institucional] for e in estudiantes_no_asignados_base if e.identificador_institucional in indice_estudiante]


def servicio_procesar_mtn(archivo, periodo_de_nivelacion: PeriodoDeNivelacion):
    from usuarios.models import UsuarioDeSistema
    from academico.models import Carrera, Campus

    libro = openpyxl.load_workbook(archivo)
    hoja = libro.active
    registros_totales = 0
    registros_validos = 0
    registros_observados = 0
    filas_observadas = []

    for fila in hoja.iter_rows(min_row=2, values_only=True):
        registros_totales += 1
        try:
            identificacion = fila[0]
            nombres = fila[1]
            apellidos = fila[2]
            correo_institucional = fila[3]
            carrera_nombre = fila[4]
            campus_nombre = fila[5]
            jornada = fila[6]
            registro_de_cupo = fila[7]

            if not all([identificacion, nombres, apellidos, correo_institucional, carrera_nombre, campus_nombre, jornada, registro_de_cupo]):
                raise ValueError("Existen criterios vacíos.")

            carrera = Carrera.objects.filter(nombre__iexact=str(carrera_nombre)).first()
            campus = Campus.objects.filter(nombre__iexact=str(campus_nombre)).first()

            if not carrera or not campus:
                raise ValueError(f"Carrera o campus no registrado ({carrera_nombre}/{campus_nombre}).")

            if UsuarioDeSistema.objects.filter(identificacion=str(identificacion)).exists():
                raise ValueError(f"Número de identificación existente: {identificacion}")

            usuario = UsuarioDeSistema.objects.create_user(
                correo_institucional = str(correo_institucional),
                password = str(identificacion),
                identificacion = str(identificacion),
                nombres = str(nombres),
                apellidos = str(apellidos),
            )
            PerfilEstudiante.objects.create(
                usuario_de_sistema = usuario,
                identificador_institucional = str(identificacion),
                numero_de_matricula = str(identificacion),
                jornada = str(jornada),
                registro_de_cupo = str(registro_de_cupo),
                carrera_registrada = carrera,
                campus_registrado = campus,
                estado_de_matricula = EstadoDeMatricula.ASPIRANTE.value,
            )
            registros_validos += 1

        except Exception as error:
            registros_observados += 1
            filas_observadas.append(f"Fila {registros_totales + 1} ({error})")

    ConsolidadoAcademico.objects.update_or_create(
        periodo_academico = periodo_de_nivelacion,
        defaults = {
            "fecha_de_corte": date.today(),
            "total_cupos_aceptados": registros_validos,
            "registros_totales": registros_totales,
            "registros_validos": registros_validos,
            "registros_observados": registros_observados,
        }
    )
    return {
        "registros_totales": registros_totales,
        "registros_validos": registros_validos,
        "registros_observados": registros_observados,
        "filas_observadas": filas_observadas,
    }


def servicio_exportar_informe(informe_general: InformeGeneral, formato: str):
    evaluaciones = EvaluacionAcademica.objects.filter(
        unidad_curricular__malla_curricular__carrera__campus__universidad=informe_general.periodo_academico.universidad
    ).select_related("estudiante", "unidad_curricular")

    if formato == "excel":
        return _exportar_excel(informe_general, evaluaciones)
    return _exportar_txt(informe_general, evaluaciones)


def _exportar_excel(informe_django, evaluaciones):
    libro = openpyxl.Workbook()
    hoja = libro.active
    hoja.title = f"Informe {informe_django.periodo_academico.periodo}"
    hoja.append(["Identificación", "Nombres", "Apellidos", "Carrera registrada", "Campus registrado",
                 "Jornada", "Unidad curricular", "Calificación primer parcial", "Calificación segundo parcial",
                 "Calificacion final", "Porcentaje de asistencia final", "Estado"])
    for evaluacion in evaluaciones:
        evaluacion_estudiante = evaluacion.estudiante
        hoja.append([
            evaluacion_estudiante.usuario_de_sistema.identificacion,
            evaluacion_estudiante.usuario_de_sistema.nombres,
            evaluacion_estudiante.usuario_de_sistema.apellidos,
            evaluacion_estudiante.carrera_registrada.nombre,
            evaluacion_estudiante.campus_registrado.nombre,
            evaluacion_estudiante.jornada,
            evaluacion.unidad_curricular.nombre,
            evaluacion.calificacion_parcial_1,
            evaluacion.calificacion_parcial_2,
            evaluacion.nota_final,
            evaluacion.porcentaje_asistencia,
            evaluacion.estado_de_aprobacion,
        ])
    documento = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    documento["Content-Disposition"] = f'attachment; filename="informe_{informe_django.periodo_academico.periodo}.xlsx"'
    libro.save(documento)
    return documento


def _exportar_txt(informe_django, evaluaciones):
    lineas = [
        "INFORME GENERAL DE PERIODO DE NIVELACIÓN",
        f"Periodo de nivelación: {informe_django.periodo_academico.periodo}",
        f"Universidad: {informe_django.periodo_academico.universidad.nombre}",
        f"Fecha de emisión: {date.today()}",
        "─" * 60,
    ]
    for evaluacion in evaluaciones:
        evaluacion_estudiante = evaluacion.estudiante
        lineas.append(
            f"{evaluacion_estudiante.usuario_de_sistema.identificacion:<15} "
            f"{evaluacion_estudiante.usuario_de_sistema.nombres:<25} "
            f"{evaluacion.unidad_curricular.nombre:<30} "
            f"{evaluacion.nota_final:>6.2f} "
            f"{evaluacion.estado_de_aprobacion:<12}"
        )
    documento = HttpResponse("\n".join(lineas), content_type="text/plain; charset=utf-8")
    documento["Content-Disposition"] = f'attachment; filename="informe_{informe_django.periodo_academico.periodo}.txt"'
    return documento


#MallaCurricular
def servicio_clonar_malla_curricular(id_malla_curricular_bd: int, nuevo_id: str, nueva_version_de_malla: str):
    from poo.clases.malla_curricular import MallaCurricular as MallaCurricularBase
    
    malla_curricular_db = MallaCurricular.objects.get(id=id_malla_curricular_bd)
    
    malla_curricular_base = MallaCurricularBase(
        codigo_de_malla=malla_curricular_db.codigo_de_malla,
        nombre=malla_curricular_db.nombre,
        area_de_conocimiento=malla_curricular_db.area_de_conocimiento,
        duracion_semanas=malla_curricular_db.duracion_semanas,
        version_de_malla=malla_curricular_db.version_de_malla,
        modalidad=Modalidad(malla_curricular_db.modalidad)
    )

    malla_curricular_clonada_base = malla_curricular_base.clonar(nuevo_id, nueva_version_de_malla)

    nueva_malla_curricular_db = MallaCurricular.objects.create(
        carrera=malla_curricular_db.carrera,
        codigo_de_malla=malla_curricular_clonada_base.codigo_de_malla,
        nombre=malla_curricular_clonada_base.nombre,
        area_de_conocimiento=malla_curricular_clonada_base.area_de_conocimiento,
        duracion_semanas=malla_curricular_clonada_base.duracion_semanas,
        version_de_malla=malla_curricular_clonada_base.version_de_malla,
        modalidad=malla_curricular_clonada_base.modalidad.value,
        estado=malla_curricular_clonada_base._estado.value,
        total_horas_nivelacion=malla_curricular_clonada_base._total_horas_nivelacion
    )
    
    return nueva_malla_curricular_db