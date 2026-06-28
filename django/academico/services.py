import openpyxl
import unicodedata
from datetime import date, datetime
from django.db import transaction
from django.http import HttpResponse

from academico.models import Campus, Carrera, PeriodoDeNivelacion, Paralelo, EvaluacionAcademica, CohorteDeMatricula, InformeGeneral, ConsolidadoAcademico, MatriculaParalelo, Horario, MallaCurricular
from usuarios.models import PerfilEstudiante
from usuarios.utils import generar_identificador_siguiente

# Enums
from poo.clases.enums.estado_de_matricula import EstadoDeMatricula
from poo.clases.enums.estado_de_aprobacion import EstadoDeAprobacion
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo
from poo.clases.enums.formato_de_exportacion import FormatoDeExportacion
from poo.clases.enums.modalidad import Modalidad
from poo.clases.enums.jornada import Jornada
from poo.clases.enums.tipo_de_cohorte import TipoDeCohorte
from poo.clases.enums.dia_de_semana import DiaDeSemana
from poo.clases.enums.tipo_de_sesion import TipoDeSesion

# POO
from poo.clases.carrera import Carrera as CarreraBase
from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion as PeriodoDeNivelacionBase
from poo.clases.evaluacion_academica import EvaluacionAcademica as EvaluacionAcademicaPOO # Evitar choque de nombres
from poo.clases.informe_general import InformeGeneral as InformeGeneralPOO
from poo.clases.servicios.procesador_de_informe import ProcesadorDeInforme
from poo.clases.cohorte_de_matricula import CohorteDeMatricula as CohorteDeMatriculaPOO
from poo.clases.horario import Horario as HorarioPOO
from poo.clases.servicios.distribuidor_de_estudiantes import DistribuidorDeEstudiantes
from poo.clases.consolidado_academico import ConsolidadoAcademico as ConsolidadoAcademicoPOO

from academico.models import (
    Campus, Carrera, PeriodoDeNivelacion, Paralelo, EvaluacionAcademica,
    CohorteDeMatricula, InformeGeneral, ConsolidadoAcademico, MatriculaParalelo,
    Horario, MallaCurricular, UnidadCurricular )

from poo.clases.enums.estado_de_malla import EstadoDeMalla


def normalizar_texto(texto):
    if not texto:
        return ""
    texto = str(texto).strip().lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto

def obtener_enum_flexible(enum_class, valor_sucio):
    if not valor_sucio:
        return None
    valor_normalizado = normalizar_texto(valor_sucio)
    for opcion in enum_class:
        if normalizar_texto(opcion.value) == valor_normalizado:
            return opcion
    raise ValueError(f"'{valor_sucio}' registro no válido para {enum_class.__name__}")

#Campus
def servicio_campus_registrar_masivo_desde_excel(archivo, universidad_usuario):
    from poo.clases.campus import Campus as CampusBase

    resultado = {"exitosos": 0, "advertencias": [], "error": None}
    try:
        wb = openpyxl.load_workbook(archivo)
        ws = wb.active

        nombres_registrados = {
            CampusBase.normalizar_nombre(nombre_existente)
            for nombre_existente in Campus.objects.filter(
                universidad=universidad_usuario
            ).values_list("nombre", flat=True)
        }

        for numero_fila, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                nombre, direccion, provincia = fila[0], fila[1], fila[2]
                if not nombre and not direccion and not provincia: continue
                if not nombre or not direccion or not provincia:
                    resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido por falta de información")
                    continue

                nombre_normalizado = CampusBase.normalizar_nombre(nombre)
                if nombre_normalizado in nombres_registrados:
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (el Campus ya existe)"
                    )
                    continue

                with transaction.atomic():
                    Campus.objects.create(
                        universidad=universidad_usuario,
                        codigo_de_campus=generar_identificador_siguiente(Campus, 'CAM', 'codigo_de_campus'),
                        nombre=nombre,
                        direccion_fisica=direccion,
                        provincia=provincia
                    )
                    resultado["exitosos"] += 1
                    nombres_registrados.add(nombre_normalizado)
            except Exception as e:
                resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido({str(e)})")
                
    except Exception:
        resultado["error"] = "Ha ocurrido un error al procesar el documento"
        
    return resultado


#Carrera
def servicio_carrera_registrar_masivo_desde_excel(archivo, universidad_usuario):
    resultado = {"exitosos": 0, "advertencias": [], "error": None}
    try:
        wb = openpyxl.load_workbook(archivo)
        ws = wb.active
        
        campus_existente = Campus.objects.filter(universidad=universidad_usuario)

        carreras_registradas = {
            (campus_id, CarreraBase.normalizar_nombre(nombre_existente))
            for campus_id, nombre_existente in Carrera.objects.filter(
                campus__universidad=universidad_usuario
            ).values_list("campus_id", "nombre")
        }

        for numero_fila, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                codigo_campus, nombre, modalidad, facultad, vigencia = fila[:5]
                
                if not codigo_campus and not nombre and not modalidad and not facultad and not vigencia:
                    continue
                
                if not codigo_campus or not nombre or not modalidad or not facultad or not vigencia:
                    resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido por falta de información")
                    continue

                try:
                    enum_modalidad = obtener_enum_flexible(Modalidad, modalidad)
                except ValueError:
                    resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido (Modalidad no válida)")
                    continue

                if isinstance(vigencia, (datetime, date)):
                    vigencia_date = vigencia.date() if isinstance(vigencia, datetime) else vigencia
                elif isinstance(vigencia, str):
                    try:
                        vigencia_date = datetime.strptime(vigencia.strip(), "%Y-%m-%d").date()
                    except ValueError:
                        resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido (formato de fecha no válido)")
                        continue
                else:
                    resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido (formato de fecha no válido)")
                    continue

                campus_obj = campus_existente.filter(codigo_de_campus=codigo_campus).first()
                if not campus_obj:
                    resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido (código de Campus no válido)")
                    continue
                
                carrera_poo = CarreraBase(
                    codigo_de_carrera="PENDIENTE",
                    nombre=nombre,
                    modalidad=enum_modalidad,
                    facultad=facultad,
                    vigencia_sniese=vigencia_date
                )

                if not carrera_poo.esta_activa():
                    resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido (Carrera no vigente)")
                    continue

                clave_carrera = (campus_obj.id, CarreraBase.normalizar_nombre(nombre))
                if clave_carrera in carreras_registradas:
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (la Carrera ya existe)"
                    )
                    continue

                with transaction.atomic():
                    Carrera.objects.create(
                        campus=campus_obj,
                        codigo_de_carrera=generar_identificador_siguiente(Carrera, 'CAR', 'codigo_de_carrera'),
                        nombre=nombre,
                        modalidad=enum_modalidad.value, 
                        facultad=facultad,
                        vigencia_sniese=vigencia_date
                    )
                    resultado["exitosos"] += 1
                    carreras_registradas.add(clave_carrera)
            except Exception as e:
                resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido ({str(e)})")
                
    except Exception:
        resultado["error"] = "Ha ocurrido un error al procesar el documento"
        
    return resultado



#PeriodoDeNivelacion 
def _construir_periodo(periodo_db):
    return PeriodoDeNivelacionBase(
        codigo_periodo=periodo_db.codigo_periodo,
        anio=periodo_db.anio,
        periodo=periodo_db.periodo,
        fecha_inicio=periodo_db.fecha_inicio,
        fecha_fin=periodo_db.fecha_fin,
        modalidad=obtener_enum_flexible(Modalidad, periodo_db.modalidad),
        numero_periodo=periodo_db.numero_periodo,
        estado=obtener_enum_flexible(EstadoDePeriodo, periodo_db.estado)
    )

def servicio_iniciar_periodo_de_nivelacion(periodo_db):
    from poo.clases.servicios.centro_de_operacion_academica import CentroDeOperacionAcademica
    periodo_poo = _construir_periodo(periodo_db)
    facade = CentroDeOperacionAcademica()
    if facade.iniciar_periodo(periodo_poo):
        periodo_db.estado = periodo_poo.estado.value
        periodo_db.save()
        return True
    return False

def servicio_finalizar_periodo_de_nivelacion(periodo_db):
    from poo.clases.servicios.centro_de_operacion_academica import CentroDeOperacionAcademica
    periodo_poo = _construir_periodo(periodo_db)
    facade = CentroDeOperacionAcademica()
    if facade.finalizar_periodo(periodo_poo):
        periodo_db.estado = periodo_poo.estado.value
        periodo_db.save()
        return True
    return False


#Malla curricular
def servicio_malla_registrar_masivo_desde_excel(archivo, universidad_usuario):
    from poo.clases.malla_curricular import MallaCurricular as MallaCurricularBase
    from poo.clases.enums.estado_de_malla import EstadoDeMalla

    resultado = {"exitosos": 0, "advertencias": [], "error": None}
    try:
        wb = openpyxl.load_workbook(archivo)
        ws = wb.active

        carreras_existentes = Carrera.objects.filter(campus__universidad=universidad_usuario)

        mallas_registradas = {
            (carrera_id, str(nombre_existente).strip().lower())
            for carrera_id, nombre_existente in MallaCurricular.objects.filter(
                carrera__campus__universidad=universidad_usuario
            ).values_list("carrera_id", "nombre")
        }

        for numero_fila, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                codigo_carrera, nombre, duracion = fila[:3]

                if not any([codigo_carrera, nombre, duracion]):
                    continue

                if not all([codigo_carrera, nombre, duracion]):
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido por falta de información"
                    )
                    continue

                try:
                    duracion_int = int(duracion)
                except (ValueError, TypeError):
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (Duración no válida)"
                    )
                    continue

                carrera_obj = carreras_existentes.filter(
                    codigo_de_carrera=str(codigo_carrera).strip()
                ).first()
                if not carrera_obj:
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (Código de Carrera no válido)"
                    )
                    continue

                malla_poo = MallaCurricularBase(
                    codigo_de_malla="PENDIENTE",
                    nombre=str(nombre).strip(),
                    duracion_semanas=duracion_int,
                    version_de_malla="PENDIENTE",
                )

                errores_poo = malla_poo.validar_datos_de_registro()
                if errores_poo:
                    primer_error = list(errores_poo.values())[0]
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido ({primer_error})"
                    )
                    continue

                clave_malla = (carrera_obj.id, malla_poo.nombre.strip().lower())
                if clave_malla in mallas_registradas:
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (La Malla curricular ya existe)"
                    )
                    continue

                with transaction.atomic():
                    MallaCurricular.objects.create(
                        carrera=carrera_obj,
                        codigo_de_malla=generar_identificador_siguiente(
                            MallaCurricular, "MC", "codigo_de_malla"
                        ),
                        nombre=malla_poo.nombre,
                        duracion_semanas=malla_poo.duracion_semanas,
                        version_de_malla=servicio_generar_version_malla(carrera_obj),
                        estado=EstadoDeMalla.DISENO.value,
                    )
                    resultado["exitosos"] += 1
                    mallas_registradas.add(clave_malla)

            except Exception as e:
                resultado["advertencias"].append(
                    f"El registro de la fila {numero_fila} fue omitido ({str(e)})"
                )

    except Exception:
        resultado["error"] = "Ha ocurrido un error al procesar el documento"

    return resultado



def servicio_unidad_registrar_masivo_desde_excel(archivo, universidad_usuario):
    from poo.clases.unidad_curricular import UnidadCurricular as UnidadCurricularBase
    from poo.clases.enums.estado_de_malla import EstadoDeMalla
    from academico.models import UnidadCurricular, MallaCurricular
    from usuarios.utils import generar_identificador_siguiente

    estados_editables = (EstadoDeMalla.DISENO.value, EstadoDeMalla.ACTIVA.value)

    resultado = {"exitosos": 0, "advertencias": [], "error": None}
    try:
        wb = openpyxl.load_workbook(archivo)
        ws = wb.active

        mallas_existentes = MallaCurricular.objects.filter(
            carrera__campus__universidad=universidad_usuario
        )

        unidades_registradas = {
            (malla_id, str(nombre_u).strip().lower())
            for malla_id, nombre_u in UnidadCurricular.objects.filter(
                malla_curricular__carrera__campus__universidad=universidad_usuario
            ).values_list("malla_curricular_id", "nombre")
        }

        for numero_fila, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                (codigo_malla, nombre, areas_str, horas_totales,
                 horas_sincronicas, horas_asincronicas,
                 criterio, porcentaje_asistencia) = fila[:8]

                if not any([codigo_malla, nombre, areas_str, horas_totales,
                            horas_sincronicas, horas_asincronicas]):
                    continue

                if not all([codigo_malla, nombre, areas_str, horas_totales,
                            horas_sincronicas, horas_asincronicas]):
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido por falta de información"
                    )
                    continue

                try:
                    horas_totales_f = float(horas_totales)
                    horas_sincronicas_f = float(horas_sincronicas)
                    horas_asincronicas_f = float(horas_asincronicas)
                    criterio_f = float(criterio) if criterio is not None else 7.0
                    porcentaje_f = float(porcentaje_asistencia) if porcentaje_asistencia is not None else 70.0
                except (ValueError, TypeError):
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (registro(s) no válido(s))"
                    )
                    continue

                malla_obj = mallas_existentes.filter(
                    codigo_de_malla=str(codigo_malla).strip()
                ).first()
                if not malla_obj:
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (Código de Malla no válido)"
                    )
                    continue

                if malla_obj.estado not in estados_editables:
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (Estado no válido)"
                    )
                    continue

                clave_unidad = (malla_obj.id, str(nombre).strip().lower())
                if clave_unidad in unidades_registradas:
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (la Unidad curricular ya existe en la Malla especificada)"
                    )
                    continue

                areas_lista = [a.strip() for a in str(areas_str).split(",") if a.strip()]

                unidad_poo = UnidadCurricularBase(
                    codigo_de_unidad="PENDIENTE",
                    nombre=str(nombre).strip(),
                    area_de_conocimiento=areas_lista,
                    horas_totales=horas_totales_f,
                    horas_sincronicas=horas_sincronicas_f,
                    horas_asincronicas=horas_asincronicas_f,
                    criterio_de_aprobacion=criterio_f,
                    porcentaje_minimo_asistencia=porcentaje_f,
                )

                errores_poo = unidad_poo.validar_datos_de_registro()
                if errores_poo:
                    primer_error = list(errores_poo.values())[0]
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido ({primer_error})"
                    )
                    continue

                with transaction.atomic():
                    UnidadCurricular.objects.create(
                        malla_curricular=malla_obj,
                        codigo_de_unidad=generar_identificador_siguiente(
                            UnidadCurricular, "UC", "codigo_de_unidad"
                        ),
                        nombre=unidad_poo.nombre,
                        area_de_conocimiento=unidad_poo.area_de_conocimiento,
                        horas_totales=unidad_poo.horas_totales,
                        horas_sincronicas=unidad_poo.horas_sincronicas,
                        horas_asincronicas=unidad_poo.horas_asincronicas,
                        criterio_de_aprobacion=unidad_poo.criterio_de_aprobacion,
                        porcentaje_minimo_asistencia=unidad_poo.porcentaje_minimo_asistencia,
                    )
                    resultado["exitosos"] += 1
                    unidades_registradas.add(clave_unidad)

            except Exception as e:
                resultado["advertencias"].append(
                    f"El registro de la fila {numero_fila} fue omitido ({str(e)})"
                )

    except Exception:
        resultado["error"] = "Ha ocurrido un error al procesar el documento"

    return resultado





def servicio_registrar_evaluacion_academica(evaluacion_academica: EvaluacionAcademica):
    from poo.clases.unidad_curricular import UnidadCurricular as UnidadCurricularBase
    from usuarios.services import _construir_estudiante

    unidad_curricular_base = UnidadCurricularBase(
        codigo_de_unidad = evaluacion_academica.unidad_curricular.codigo_de_unidad,
        nombre = evaluacion_academica.unidad_curricular.nombre,
        area_de_conocimiento = evaluacion_academica.unidad_curricular.area_de_conocimiento,
        horas_totales = evaluacion_academica.unidad_curricular.horas_totales,
        horas_sincronicas = evaluacion_academica.unidad_curricular.horas_sincronicas,
        horas_asincronicas = evaluacion_academica.unidad_curricular.horas_asincronicas,
        criterio_de_aprobacion = evaluacion_academica.unidad_curricular.criterio_de_aprobacion,
        porcentaje_minimo_asistencia = evaluacion_academica.unidad_curricular.porcentaje_minimo_asistencia
    )
    estudiante = _construir_estudiante(evaluacion_academica.estudiante)
    evaluacion = EvaluacionAcademicaPOO(estudiante = estudiante, unidad_curricular = unidad_curricular_base)
    
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

    paralelos_base = []
    indice_paralelo = {}

    for paralelo in paralelos:
        paralelo_base = ParaleloBase(
            codigo_de_paralelo = paralelo.codigo_de_paralelo,
            nombre = paralelo.nombre,
            jornada = obtener_enum_flexible(Jornada, paralelo.jornada),
            modalidad = obtener_enum_flexible(Modalidad, paralelo.modalidad),
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
    from usuarios.services import servicio_estudiante_registrar_masivo_desde_excel
    from poo.clases.consolidado_academico import ConsolidadoAcademico as ConsolidadoAcademicoPOO

    resultado = servicio_estudiante_registrar_masivo_desde_excel(
        archivo, periodo_de_nivelacion.universidad, periodo_de_nivelacion=periodo_de_nivelacion
    )


    if resultado.get("error"):
        return resultado

    matriz_procesada = [
        {"identificacion": identificacion} for identificacion in resultado["identificaciones_validas"]
    ] + [{} for _ in range(resultado["observados"])]

    consolidado_poo = ConsolidadoAcademicoPOO(
        periodo_academico=None,
        fecha_de_corte=date.today(),
        total_de_cupos_aceptados=resultado["exitosos"],
    )
    consolidado_poo.cargar_matriz_de_cupos(
        matriz_procesada, resultado["exitosos"], resultado["observados"]
    )
    estadisticas = consolidado_poo.obtener_estadisticas_de_consolidado()

    consolidado_db, _ = ConsolidadoAcademico.objects.get_or_create(
        periodo_academico=periodo_de_nivelacion,
        defaults={"fecha_de_corte": date.today()},
    )
    consolidado_db.registros_validos += estadisticas["Registros válidos"]
    consolidado_db.total_cupos_aceptados += estadisticas["Cupos aceptados esperados"]
    consolidado_db.registros_observados = estadisticas["Registros observados"]
    consolidado_db.registros_totales = consolidado_db.registros_validos + estadisticas["Registros observados"]
    consolidado_db.fecha_de_corte = date.today()
    consolidado_db.save()

    return resultado




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
def _construir_unidad_poo(unidad_db):
    from poo.clases.unidad_curricular import UnidadCurricular as UnidadCurricularBase

    return UnidadCurricularBase(
        codigo_de_unidad=unidad_db.codigo_de_unidad,
        nombre=unidad_db.nombre,
        area_de_conocimiento=unidad_db.area_de_conocimiento,
        horas_totales=unidad_db.horas_totales,
        horas_sincronicas=unidad_db.horas_sincronicas,
        horas_asincronicas=unidad_db.horas_asincronicas,
        criterio_de_aprobacion=unidad_db.criterio_de_aprobacion,
        porcentaje_minimo_asistencia=unidad_db.porcentaje_minimo_asistencia,
    )
    
def servicio_generar_version_malla(carrera):
    import re
    maximo = 0
    for version in MallaCurricular.objects.filter(carrera=carrera).values_list("version_de_malla", flat=True):
        coincidencia = re.search(r"\d+", str(version or ""))
        if coincidencia:
            maximo = max(maximo, int(coincidencia.group()))
    return f"V{maximo + 1}"
    
def _construir_malla_poo(malla_db, cargar_unidades=False):
    from poo.clases.malla_curricular import MallaCurricular as MallaCurricularBase

    malla_poo = MallaCurricularBase(
        codigo_de_malla=malla_db.codigo_de_malla,
        nombre=malla_db.nombre,
        duracion_semanas=malla_db.duracion_semanas,
        version_de_malla=malla_db.version_de_malla,
    )

    if cargar_unidades:
        for unidad_db in malla_db.unidades_curriculares.all():
            malla_poo.agregar_unidad_curricular(_construir_unidad_poo(unidad_db))

    malla_poo.establecer_estado(obtener_enum_flexible(EstadoDeMalla, malla_db.estado))
    return malla_poo

def servicio_recalcular_total_horas_malla(malla_db):
    malla_poo = _construir_malla_poo(malla_db, cargar_unidades=False)
    malla_poo.establecer_estado(EstadoDeMalla.DISENO)

    for unidad_db in malla_db.unidades_curriculares.all():
        malla_poo.agregar_unidad_curricular(_construir_unidad_poo(unidad_db))

    malla_db.total_horas_nivelacion = malla_poo.calcular_total_horas_nivelacion()
    malla_db.save(update_fields=["total_horas_nivelacion"])
    return malla_db.total_horas_nivelacion

def servicio_cambiar_estado_malla(malla_db, accion):
    malla_poo = _construir_malla_poo(malla_db)

    if accion == "activar":
        otra_activa = MallaCurricular.objects.filter(
            carrera=malla_db.carrera,
            estado=EstadoDeMalla.ACTIVA.value,
        ).exclude(pk=malla_db.pk).first()

        if otra_activa:
            return (
                False,
                f"La Carrera tiene una Malla curricular activa ({otra_activa.codigo_de_malla} - {otra_activa.version_de_malla})"
            )

        if not malla_poo.activar():
            return (False, "La Malla curricular no se ha podido habilitar")

    elif accion == "historica":
        if not malla_poo.marcar_historica():
            return (False, "La Malla curricular no se ha podido descontinuar")

    elif accion == "inactivar":
        if not malla_poo.inactivar():
            return (False, "La Malla curricular no se ha podido deshabilitar")

    else:
        return (False, "No válido")

    malla_db.estado = malla_poo.estado.value
    malla_db.save(update_fields=["estado"])
    return (True, "El estado de la Malla curricular ha sido actualizado correctamente")

def servicio_clonar_malla_curricular(id_malla_curricular_bd, nuevo_nombre=None):
    from academico.models import UnidadCurricular

    malla_curricular_db = MallaCurricular.objects.get(id=id_malla_curricular_bd)

    malla_poo = _construir_malla_poo(malla_curricular_db, cargar_unidades=True)

    nuevo_codigo = generar_identificador_siguiente(MallaCurricular, "MC", "codigo_de_malla")
    nueva_version = servicio_generar_version_malla(malla_curricular_db.carrera)
    clon_poo = malla_poo.clonar(nuevo_codigo, nueva_version)

    if nuevo_nombre and str(nuevo_nombre).strip():
        clon_poo.nombre = str(nuevo_nombre).strip()

    with transaction.atomic():
        nueva_malla_curricular_db = MallaCurricular.objects.create(
            carrera=malla_curricular_db.carrera,
            codigo_de_malla=clon_poo.codigo_de_malla,
            nombre=clon_poo.nombre,
            duracion_semanas=clon_poo.duracion_semanas,
            version_de_malla=clon_poo.version_de_malla,
            estado=clon_poo.estado.value,  # Diseño
            total_horas_nivelacion=clon_poo.total_horas_nivelacion,
        )

        for unidad_poo in clon_poo.obtener_unidades_curriculares():
            UnidadCurricular.objects.create(
                malla_curricular=nueva_malla_curricular_db,
                codigo_de_unidad=generar_identificador_siguiente(
                    UnidadCurricular, "UC", "codigo_de_unidad"
                ),
                nombre=unidad_poo.nombre,
                area_de_conocimiento=unidad_poo.area_de_conocimiento,
                horas_totales=unidad_poo.horas_totales,
                horas_sincronicas=unidad_poo.horas_sincronicas,
                horas_asincronicas=unidad_poo.horas_asincronicas,
                criterio_de_aprobacion=unidad_poo.criterio_de_aprobacion,
                porcentaje_minimo_asistencia=unidad_poo.porcentaje_minimo_asistencia,
            )

    return nueva_malla_curricular_db


def _obtener_o_crear_cohorte(periodo_db, carrera):
    from poo.clases.enums.tipo_de_cohorte import TipoDeCohorte

    cohorte = CohorteDeMatricula.objects.filter(
        periodo_de_nivelacion=periodo_db, carrera_registrada=carrera
    ).first()
    if cohorte:
        return cohorte

    return CohorteDeMatricula.objects.create(
        periodo_de_nivelacion=periodo_db,
        carrera_registrada=carrera,
        codigo_de_registro=generar_identificador_siguiente(CohorteDeMatricula, "COH", "codigo_de_registro"),
        nombre_cohorte=f"Cohorte {carrera.nombre} - {periodo_db.periodo}",
        fecha_de_cierre=periodo_db.fecha_fin,
        tipo_de_cohorte=TipoDeCohorte.PRIMERA_MATRICULA.value,
    )
def servicio_generar_paralelos(periodo_db, capacidad=35):
    import math
    from poo.clases.paralelo import Paralelo as ParaleloBase
    from poo.clases.servicios.centro_de_operacion_academica import CentroDeOperacionAcademica
    from poo.clases.enums.jornada import Jornada
    from poo.clases.enums.modalidad import Modalidad as EnumModalidad
    from poo.clases.enums.estado_de_malla import EstadoDeMalla
    from poo.clases.enums.registro_de_cupo import RegistroDeCupo

    resumen = {
        "grupos_creados": 0,
        "paralelos_creados": 0,
        "estudiantes_distribuidos": 0,
        "advertencias": [],
    }

    try:
        capacidad = int(capacidad)
    except (TypeError, ValueError):
        capacidad = 35
    if capacidad <= 0:
        capacidad = 35

    universidad = periodo_db.universidad
    facade = CentroDeOperacionAcademica()
    enum_modalidad = obtener_enum_flexible(EnumModalidad, periodo_db.modalidad)

    carreras = Carrera.objects.filter(campus__universidad=universidad)

    for carrera in carreras:
        malla = MallaCurricular.objects.filter(
            carrera=carrera, estado=EstadoDeMalla.ACTIVA.value
        ).first()
        if not malla:
            continue

        unidades = list(malla.unidades_curriculares.all())
        if not unidades:
            resumen["advertencias"].append(
                f"El registro de la Malla curricular activa de {carrera.nombre} fue omitido (no presenta Unidades curriculares)"
            )
            continue

        jornadas_presentes = (
            PerfilEstudiante.objects.filter(
                carrera_registrada=carrera, periodo_de_nivelacion=periodo_db
            )
            .values_list("jornada", flat=True).distinct()
        )


        for jornada_valor in jornadas_presentes:
            estudiantes = list(
                PerfilEstudiante.objects.filter(
                    carrera_registrada=carrera,
                    jornada=jornada_valor,
                    periodo_de_nivelacion=periodo_db,
                ).exclude(
                    estudiantes_matriculados__paralelo__periodo_de_nivelacion=periodo_db
                ).distinct()
            )
            if not estudiantes:
                continue

            try:
                enum_jornada = obtener_enum_flexible(Jornada, jornada_valor)
            except ValueError:
                resumen["advertencias"].append(
                    f"El registro de Jornada fue omitido (Jornada no válida en {carrera.nombre})"
                )
                continue

            cohorte = _obtener_o_crear_cohorte(periodo_db, carrera)
            estudiantes_a_contar = []

            def _numero_de_grupo(nombre):
                try:
                    return int(str(nombre).split()[-1])
                except (ValueError, IndexError):
                    return 0

            with transaction.atomic():
                paralelos_existentes = Paralelo.objects.filter(
                    periodo_de_nivelacion=periodo_db,
                    jornada=jornada_valor,
                    unidad_curricular__in=unidades,
                )
                grupos_existentes = {}
                for paralelo_db in paralelos_existentes:
                    grupos_existentes.setdefault(paralelo_db.nombre, []).append(paralelo_db)

                indice_max = 0
                indice_pendiente = 0

                for nombre_grupo in sorted(grupos_existentes.keys(), key=_numero_de_grupo):
                    paralelos_grupo = grupos_existentes[nombre_grupo]
                    indice_max = max(indice_max, _numero_de_grupo(nombre_grupo))

                    representativo = paralelos_grupo[0]
                    ocupacion = MatriculaParalelo.objects.filter(paralelo=representativo).count()
                    cupo_libre = representativo.capacidad_maxima - ocupacion
                    if cupo_libre <= 0:
                        continue

                    a_matricular = estudiantes[indice_pendiente:indice_pendiente + cupo_libre]
                    indice_pendiente += len(a_matricular)

                    for paralelo_db in paralelos_grupo:
                        for estudiante_db in a_matricular:
                            MatriculaParalelo.objects.create(
                                estudiante=estudiante_db,
                                paralelo=paralelo_db,
                                cohorte_de_matricula=cohorte,
                            )
                    estudiantes_a_contar.extend(a_matricular)

                estudiantes_restantes = estudiantes[indice_pendiente:]
                if estudiantes_restantes:
                    numero_de_grupos = math.ceil(len(estudiantes_restantes) / capacidad)
                    grupos_poo = [
                        ParaleloBase(
                            codigo_de_paralelo=f"G{indice}",
                            nombre=f"Paralelo {indice_max + indice}",
                            jornada=enum_jornada,
                            modalidad=enum_modalidad,
                            capacidad_maxima=capacidad,
                        )
                        for indice in range(1, numero_de_grupos + 1)
                    ]

                    facade.distribuir_estudiantes(grupos_poo, estudiantes_restantes)

                    for indice, grupo_poo in enumerate(grupos_poo, start=1):
                        miembros = list(grupo_poo._estudiantes_matriculados)
                        if not miembros:
                            continue
                        nombre_nuevo = f"Paralelo {indice_max + indice}"
                        for unidad in unidades:
                            paralelo_db = Paralelo.objects.create(
                                periodo_de_nivelacion=periodo_db,
                                unidad_curricular=unidad,
                                codigo_de_paralelo=generar_identificador_siguiente(Paralelo, "PAR", "codigo_de_paralelo"),
                                nombre=nombre_nuevo,
                                jornada=jornada_valor,
                                modalidad=periodo_db.modalidad,
                                capacidad_maxima=capacidad,
                            )
                            resumen["paralelos_creados"] += 1
                            for estudiante_db in miembros:
                                MatriculaParalelo.objects.create(
                                    estudiante=estudiante_db,
                                    paralelo=paralelo_db,
                                    cohorte_de_matricula=cohorte,
                                )
                        resumen["grupos_creados"] += 1
                        estudiantes_a_contar.extend(miembros)

                for estudiante_db in estudiantes_a_contar:
                    if estudiante_db.registro_de_cupo == RegistroDeCupo.REGULAR.value:
                        cohorte.total_primera_matricula += 1
                    elif estudiante_db.registro_de_cupo == RegistroDeCupo.SEGUNDA_MATRICULA.value:
                        cohorte.total_segunda_matricula += 1
                    elif estudiante_db.registro_de_cupo == RegistroDeCupo.EXONERACION.value:
                        cohorte.total_exonerados += 1
                    resumen["estudiantes_distribuidos"] += 1

                cohorte.save()

    return resumen

def servicio_mover_estudiante(estudiante_db, paralelo_destino_db):
    periodo = paralelo_destino_db.periodo_de_nivelacion
    carrera = paralelo_destino_db.unidad_curricular.malla_curricular.carrera
    nombre_destino = paralelo_destino_db.nombre
    jornada = paralelo_destino_db.jornada

    paralelos_destino = list(Paralelo.objects.filter(
        periodo_de_nivelacion=periodo,
        jornada=jornada,
        nombre=nombre_destino,
        unidad_curricular__malla_curricular__carrera=carrera,
    ))
    if not paralelos_destino:
        return (False, "El paralelo de destino no es válido")

    representativo = paralelos_destino[0]
    ocupacion_destino = MatriculaParalelo.objects.filter(
        paralelo=representativo
    ).exclude(estudiante=estudiante_db).count()
    if ocupacion_destino >= representativo.capacidad_maxima:
        return (False, "El paralelo de destino no presenta cupo disponible")

    matriculas_actuales = MatriculaParalelo.objects.filter(
        estudiante=estudiante_db,
        paralelo__periodo_de_nivelacion=periodo,
        paralelo__unidad_curricular__malla_curricular__carrera=carrera,
    )

    primera_matricula = matriculas_actuales.first()
    if primera_matricula and primera_matricula.paralelo.nombre == nombre_destino:
        return (False, "El estudiante ya pertenece a ese paralelo")

    cohorte = (
        primera_matricula.cohorte_de_matricula
        if primera_matricula else _obtener_o_crear_cohorte(periodo, carrera)
    )

    with transaction.atomic():
        matriculas_actuales.delete()
        for paralelo_db in paralelos_destino:
            MatriculaParalelo.objects.get_or_create(
                estudiante=estudiante_db,
                paralelo=paralelo_db,
                defaults={"cohorte_de_matricula": cohorte},
            )

    return (True, "El estudiante fue reasignado correctamente")


# ==========================================
# B.2 - Horarios
# ==========================================
def _construir_horario_poo(horario_db):
    return HorarioPOO(
        dia_semana=obtener_enum_flexible(DiaDeSemana, horario_db.dia_semana),
        hora_inicio=horario_db.hora_inicio,
        hora_fin=horario_db.hora_fin,
        espacio_de_imparticion=horario_db.espacio_de_imparticion,
        modalidad=obtener_enum_flexible(Modalidad, horario_db.modalidad),
        numero_semana=horario_db.numero_semana,
        tipo_de_sesion=obtener_enum_flexible(TipoDeSesion, horario_db.tipo_de_sesion),
    )

def _construir_paralelo_poo_con_horarios(paralelo_db):
    from poo.clases.paralelo import Paralelo as ParaleloBase

    paralelo_poo = ParaleloBase(
        codigo_de_paralelo=paralelo_db.codigo_de_paralelo,
        nombre=paralelo_db.nombre,
        jornada=obtener_enum_flexible(Jornada, paralelo_db.jornada),
        modalidad=obtener_enum_flexible(Modalidad, paralelo_db.modalidad),
        capacidad_maxima=paralelo_db.capacidad_maxima,
    )
    for horario_db in Horario.objects.filter(paralelo=paralelo_db):
        paralelo_poo.agregar_horario(_construir_horario_poo(horario_db))
    return paralelo_poo

def servicio_horas_agendadas_paralelo(paralelo_db):
    return _construir_paralelo_poo_con_horarios(paralelo_db).calcular_horas_agendadas()

def servicio_registrar_horario(paralelo_db, dia_semana, hora_inicio, hora_fin, espacio, numero_semana, tipo_de_sesion):
    try:
        numero_semana = int(numero_semana)
    except (TypeError, ValueError):
        return (False, "El número de semana no es válido")

    try:
        enum_dia = obtener_enum_flexible(DiaDeSemana, dia_semana)
        enum_tipo = obtener_enum_flexible(TipoDeSesion, tipo_de_sesion)
        enum_modalidad = obtener_enum_flexible(Modalidad, paralelo_db.modalidad)
    except ValueError:
        return (False, "Día/Tipo de sesión o Modalidad no válido")

    nuevo_horario_poo = HorarioPOO(
        dia_semana=enum_dia,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        espacio_de_imparticion=espacio,
        modalidad=enum_modalidad,
        numero_semana=numero_semana,
        tipo_de_sesion=enum_tipo,
    )

    errores_horario = nuevo_horario_poo.validar_datos_de_registro()
    if errores_horario:
        return (False, list(errores_horario.values())[0])

    carrera = paralelo_db.unidad_curricular.malla_curricular.carrera
    paralelos_del_grupo = Paralelo.objects.filter(
        periodo_de_nivelacion=paralelo_db.periodo_de_nivelacion,
        jornada=paralelo_db.jornada,
        nombre=paralelo_db.nombre,
        unidad_curricular__malla_curricular__carrera=carrera,
    )
    horarios_externos = [
        _construir_horario_poo(horario_db)
        for horario_db in Horario.objects.filter(
            paralelo__in=paralelos_del_grupo
        ).exclude(paralelo=paralelo_db)
    ]

    paralelo_poo = _construir_paralelo_poo_con_horarios(paralelo_db)
    horas_sincronicas = paralelo_db.unidad_curricular.horas_sincronicas
    resultado = paralelo_poo.validar_nuevo_horario(
        nuevo_horario_poo, horas_sincronicas, horarios_externos
    )

    if not resultado["ok"]:
        if resultado["motivo"] == "conflicto":
            conflicto = resultado["horario_en_conflicto"]
            return (
                False,
                f"Conflicto horario en {conflicto.dia_semana.value} "
                f"{conflicto.hora_inicio}–{conflicto.hora_fin} (semana {conflicto.numero_semana})"
            )
        return (
            False,
            f"La sesión ha excedido las horas sincrónicas registradas de la unidad curricular")

    Horario.objects.create(
        paralelo=paralelo_db,
        dia_semana=dia_semana,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        espacio_de_imparticion=espacio,
        modalidad=paralelo_db.modalidad,
        numero_semana=numero_semana,
        tipo_de_sesion=tipo_de_sesion,
    )
    return (True, "El horario ha sido registrado correctamente")

def servicio_obtener_matriz_de_horarios(periodo_db, paralelos_db):
    from poo.clases.servicios.centro_de_operacion_academica import CentroDeOperacionAcademica

    periodo_poo = _construir_periodo(periodo_db)
    paralelos_poo = [_construir_paralelo_poo_con_horarios(p) for p in paralelos_db]

    facade = CentroDeOperacionAcademica()
    matriz = facade.obtener_matriz_de_horarios(periodo_poo, paralelos_poo)

    mapa_unidad = {
        p.codigo_de_paralelo: p.unidad_curricular.nombre for p in paralelos_db
    }
    for fila in matriz:
        for bloque in fila["bloques"]:
            bloque["unidad"] = mapa_unidad.get(bloque["codigo_de_paralelo"], "—")

    return matriz


def _construir_docente_poo_para_periodo(docente_db, periodo_db, paralelo_excluir_id=None):
    from usuarios.services import _crear_docente
    from poo.clases.enums.estado_de_vinculacion import EstadoDeVinculacion as EnumEstadoDeVinculacion

    docente_poo = _crear_docente(docente_db)
    docente_poo.establecer_estado_de_vinculacion(
        obtener_enum_flexible(EnumEstadoDeVinculacion, docente_db.estado_de_vinculacion)
    )
    docente_poo.definir_especialidades(docente_db.especialidades or [])

    paralelos_actuales = Paralelo.objects.filter(
        periodo_de_nivelacion=periodo_db, docente_responsable=docente_db
    ).select_related("unidad_curricular")
    if paralelo_excluir_id:
        paralelos_actuales = paralelos_actuales.exclude(id=paralelo_excluir_id)

    carga_actual = 0.0
    for paralelo_actual in paralelos_actuales:
        carga_actual += paralelo_actual.unidad_curricular.horas_sincronicas
        for horario_db in Horario.objects.filter(paralelo=paralelo_actual):
            docente_poo.agregar_horario_ocupado(_construir_horario_poo(horario_db))

    docente_poo.registrar_carga_actual(carga_actual)
    return docente_poo, carga_actual

def _texto_motivo_no_asignable(resultado):
    motivo = resultado.get("motivo")
    if motivo == "inactivo":
        return "El docente no está activo"
    if motivo == "conflicto":
        conflicto = resultado["horario_en_conflicto"]
        return (
            f"Conflicto de Horario el día '{conflicto.dia_semana.value}'. {conflicto.hora_inicio}–{conflicto.hora_fin} (semana {conflicto.numero_semana})"
        )
    if motivo == "carga":
        return (
            f"El Docente excede la carga de horas máxima"
        )
    return "El Docente no puede ser asignado."

def servicio_evaluar_docentes_para_paralelo(paralelo_db):
    from usuarios.models import PerfilDocente
    from poo.clases.servicios.centro_de_operacion_academica import CentroDeOperacionAcademica

    periodo = paralelo_db.periodo_de_nivelacion
    unidad = paralelo_db.unidad_curricular
    areas = unidad.area_de_conocimiento or []
    horas_unidad = unidad.horas_sincronicas

    paralelo_poo = _construir_paralelo_poo_con_horarios(paralelo_db)
    facade = CentroDeOperacionAcademica()

    docentes = PerfilDocente.objects.filter(
        universidad=periodo.universidad
    ).select_related("usuario_de_sistema").order_by(
        "usuario_de_sistema__apellidos", "usuario_de_sistema__nombres"
    )

    evaluaciones = []
    for docente_db in docentes:
        docente_poo, carga_actual = _construir_docente_poo_para_periodo(
            docente_db, periodo, paralelo_excluir_id=paralelo_db.id
        )
        resultado = facade.validar_asignacion_docente(
            docente_poo, paralelo_poo, horas_unidad, areas
        )
        evaluaciones.append({
            "docente": docente_db,
            "es_actual": paralelo_db.docente_responsable_id == docente_db.id,
            "carga_actual": carga_actual,
            "carga_maxima": docente_db.carga_horaria_maxima,
            "horas_unidad": horas_unidad,
            "asignable": resultado["ok"],
            "motivo": "" if resultado["ok"] else _texto_motivo_no_asignable(resultado),
            "especialidad_ok": docente_poo.tiene_especialidad_para(areas),
            "activo": docente_poo.esta_activo(),
        })
    return evaluaciones

def servicio_asignar_docente(paralelo_db, docente_db):
    from poo.clases.servicios.centro_de_operacion_academica import CentroDeOperacionAcademica

    periodo = paralelo_db.periodo_de_nivelacion
    unidad = paralelo_db.unidad_curricular
    areas = unidad.area_de_conocimiento or []
    horas_unidad = unidad.horas_sincronicas

    docente_poo, carga_actual = _construir_docente_poo_para_periodo(
        docente_db, periodo, paralelo_excluir_id=paralelo_db.id
    )
    paralelo_poo = _construir_paralelo_poo_con_horarios(paralelo_db)

    facade = CentroDeOperacionAcademica()
    resultado = facade.validar_asignacion_docente(docente_poo, paralelo_poo, horas_unidad, areas)

    if not resultado["ok"]:
        return (False, _texto_motivo_no_asignable(resultado), None)

    paralelo_db.docente_responsable = docente_db
    paralelo_db.save(update_fields=["docente_responsable"])

    docente_db.carga_horaria_actual = round(carga_actual + horas_unidad, 2)
    docente_db.save(update_fields=["carga_horaria_actual"])

    advertencia = None
    if resultado.get("advertencia") == "especialidad":
        advertencia = ("El área de conocimiento de la Unidad curricular no coincide con las especialidades registradas del Docente")
    return (True, "El Docente ha sido asignado correctamente", advertencia)

def servicio_quitar_docente(paralelo_db):
    if not docente_db:
        return (False, "El paralelo no tiene un docente designado actualmente")

    horas_unidad = paralelo_db.unidad_curricular.horas_sincronicas
    paralelo_db.docente_responsable = None
    paralelo_db.save(update_fields=["docente_responsable"])

    carga_restante = max(0.0, round((docente_db.carga_horaria_actual or 0) - horas_unidad, 2))
    docente_db.carga_horaria_actual = carga_restante
    docente_db.save(update_fields=["carga_horaria_actual"])

    return (True, "El Docente ha sido desvinculado correctamente")
