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
from poo.clases.enums.tipo_de_componente import TipoDeComponente
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
    resultado = {"exitosos": 0, "advertencias": [], "error": None}
    try:
        wb = openpyxl.load_workbook(archivo)
        ws = wb.active
        
        for numero_fila, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                nombre, direccion, provincia = fila[0], fila[1], fila[2]
                if not nombre and not direccion and not provincia: continue
                if not nombre or not direccion or not provincia:
                    resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido por falta de información")
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
            except Exception as e:
                resultado["advertencias"].append(f"Fila {numero_fila} omitida ({str(e)})")
                
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
                    resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido ('{modalidad}' no es una modalidad válida)")
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
                    resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido (código de campus no válido)")
                    continue
                
                carrera_poo = CarreraBase(
                    codigo_de_carrera="PENDIENTE",
                    nombre=nombre,
                    modalidad=enum_modalidad,
                    facultad=facultad,
                    vigencia_sniese=vigencia_date
                )

                if not carrera_poo.esta_activa():
                    resultado["advertencias"].append(f"El registro de la fila {numero_fila} fue omitido (la carrera '{nombre}' no está vigente)")
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
    periodo_poo = _construir_periodo(periodo_db)
    if periodo_poo.iniciar_periodo_de_nivelacion():
        periodo_db.estado = periodo_poo.estado.value
        periodo_db.save()
        return True
    return False

def servicio_finalizar_periodo_de_nivelacion(periodo_db):
    periodo_poo = _construir_periodo(periodo_db)
    if periodo_poo.finalizar_periodo_de_nivelacion():
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

        for numero_fila, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                codigo_carrera, nombre, area, duracion, version, modalidad_str = fila[:6]

                if not any([codigo_carrera, nombre, area, duracion, version, modalidad_str]):
                    continue

                if not all([codigo_carrera, nombre, area, duracion, version, modalidad_str]):
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido por falta de información"
                    )
                    continue

                try:
                    enum_modalidad = obtener_enum_flexible(Modalidad, modalidad_str)
                except ValueError:
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (modalidad no válida)"
                    )
                    continue

                try:
                    duracion_int = int(duracion)
                except (ValueError, TypeError):
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (duración no válida)"
                    )
                    continue

                carrera_obj = carreras_existentes.filter(
                    codigo_de_carrera=str(codigo_carrera).strip()
                ).first()
                if not carrera_obj:
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (código de carrera no válido)"
                    )
                    continue

                malla_poo = MallaCurricularBase(
                    codigo_de_malla="PENDIENTE",
                    nombre=str(nombre).strip(),
                    area_de_conocimiento=str(area).strip(),
                    duracion_semanas=duracion_int,
                    version_de_malla=str(version).strip(),
                    modalidad=enum_modalidad,
                )

                errores_poo = malla_poo.validar_datos_de_registro()
                if errores_poo:
                    primer_error = list(errores_poo.values())[0]
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido ({primer_error})"
                    )
                    continue

                with transaction.atomic():
                    MallaCurricular.objects.create(
                        carrera=carrera_obj,
                        codigo_de_malla=generar_identificador_siguiente(
                            MallaCurricular, "MC", "codigo_de_malla"
                        ),
                        nombre=malla_poo.nombre,
                        area_de_conocimiento=malla_poo.area_de_conocimiento,
                        duracion_semanas=malla_poo.duracion_semanas,
                        version_de_malla=malla_poo.version_de_malla,
                        modalidad=malla_poo.modalidad.value,
                        estado=EstadoDeMalla.DISENO.value,
                    )
                    resultado["exitosos"] += 1

            except Exception as e:
                resultado["advertencias"].append(
                    f"El registro de la fila {numero_fila} fue omitido ({str(e)})"
                )

    except Exception:
        resultado["error"] = "Ha ocurrido un error al procesar el documento"

    return resultado


# Agregar en django/academico/services.py

def servicio_unidad_registrar_masivo_desde_excel(archivo, universidad_usuario):
    from poo.clases.unidad_curricular import UnidadCurricular as UnidadCurricularBase
    from poo.clases.enums.tipo_de_componente import TipoDeComponente
    from academico.models import UnidadCurricular, MallaCurricular
    from usuarios.utils import generar_identificador_siguiente

    resultado = {"exitosos": 0, "advertencias": [], "error": None}
    try:
        wb = openpyxl.load_workbook(archivo)
        ws = wb.active

        mallas_existentes = MallaCurricular.objects.filter(
            carrera__campus__universidad=universidad_usuario
        )

        for numero_fila, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                (codigo_malla, nombre, areas_str, horas_totales, horas_semanales,
                 horas_sincronicas, horas_asincronicas, tipo_componente_str,
                 criterio, porcentaje_asistencia) = fila[:10]

                if not any([codigo_malla, nombre, areas_str, horas_totales, horas_semanales,
                            horas_sincronicas, horas_asincronicas, tipo_componente_str]):
                    continue

                if not all([codigo_malla, nombre, areas_str, horas_totales, horas_semanales,
                            horas_sincronicas, horas_asincronicas, tipo_componente_str]):
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido por falta de información"
                    )
                    continue

                try:
                    enum_tipo = obtener_enum_flexible(TipoDeComponente, tipo_componente_str)
                except ValueError:
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido "
                        f"(tipo de componente no válido)"
                    )
                    continue

                try:
                    horas_totales_f = float(horas_totales)
                    horas_semanales_f = float(horas_semanales)
                    horas_sincronicas_f = float(horas_sincronicas)
                    horas_asincronicas_f = float(horas_asincronicas)
                    criterio_f = float(criterio) if criterio is not None else 7.0
                    porcentaje_f = float(porcentaje_asistencia) if porcentaje_asistencia is not None else 70.0
                except (ValueError, TypeError):
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (registro de valor no válido)"
                    )
                    continue

                malla_obj = mallas_existentes.filter(
                    codigo_de_malla=str(codigo_malla).strip()
                ).first()
                if not malla_obj:
                    resultado["advertencias"].append(
                        f"El registro de la fila {numero_fila} fue omitido (código de malla no válido)"
                    )
                    continue

                areas_lista = [a.strip() for a in str(areas_str).split(",") if a.strip()]

                # Validación a través de la capa POO
                unidad_poo = UnidadCurricularBase(
                    codigo_de_unidad="PENDIENTE",
                    nombre=str(nombre).strip(),
                    area_de_conocimiento=areas_lista,
                    horas_totales=horas_totales_f,
                    horas_semanales=horas_semanales_f,
                    horas_sincronicas=horas_sincronicas_f,
                    horas_asincronicas=horas_asincronicas_f,
                    tipo_de_componente=enum_tipo,
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
                        horas_semanales=unidad_poo.horas_semanales,
                        horas_sincronicas=unidad_poo.horas_sincronicas,
                        horas_asincronicas=unidad_poo.horas_asincronicas,
                        tipo_de_componente=unidad_poo.tipo_de_componente.value,
                        criterio_de_aprobacion=unidad_poo.criterio_de_aprobacion,
                        porcentaje_minimo_asistencia=unidad_poo.porcentaje_minimo_asistencia,
                    )
                    resultado["exitosos"] += 1

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
        horas_semanales = evaluacion_academica.unidad_curricular.horas_semanales,
        horas_sincronicas = evaluacion_academica.unidad_curricular.horas_sincronicas,
        horas_asincronicas = evaluacion_academica.unidad_curricular.horas_asincronicas,
        tipo_de_componente = obtener_enum_flexible(TipoDeComponente, evaluacion_academica.unidad_curricular.tipo_de_componente),
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
    from usuarios.models import UsuarioDeSistema

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
def _construir_unidad_poo(unidad_db):
    from poo.clases.unidad_curricular import UnidadCurricular as UnidadCurricularBase

    return UnidadCurricularBase(
        codigo_de_unidad=unidad_db.codigo_de_unidad,
        nombre=unidad_db.nombre,
        area_de_conocimiento=unidad_db.area_de_conocimiento,
        horas_totales=unidad_db.horas_totales,
        horas_semanales=unidad_db.horas_semanales,
        horas_sincronicas=unidad_db.horas_sincronicas,
        horas_asincronicas=unidad_db.horas_asincronicas,
        tipo_de_componente=obtener_enum_flexible(TipoDeComponente, unidad_db.tipo_de_componente),
        criterio_de_aprobacion=unidad_db.criterio_de_aprobacion,
        porcentaje_minimo_asistencia=unidad_db.porcentaje_minimo_asistencia,
    )

def _construir_malla_poo(malla_db, cargar_unidades=False):
    from poo.clases.malla_curricular import MallaCurricular as MallaCurricularBase

    malla_poo = MallaCurricularBase(
        codigo_de_malla=malla_db.codigo_de_malla,
        nombre=malla_db.nombre,
        area_de_conocimiento=malla_db.area_de_conocimiento,
        duracion_semanas=malla_db.duracion_semanas,
        version_de_malla=malla_db.version_de_malla,
        modalidad=obtener_enum_flexible(Modalidad, malla_db.modalidad),
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
                f"La carrera tiene una malla curricular activa ({otra_activa.codigo_de_malla} - "
                f"{otra_activa.version_de_malla}). Marcarla como histórica o inactiva"
            )

        if not malla_poo.activar():
            return (False, "La malla curricular no puede activarse desde su estado actual")

    elif accion == "historica":
        if not malla_poo.marcar_historica():
            return (False, "Sólo una malla curricular activa puede cambiar su estado a histórico")

    elif accion == "inactivar":
        if not malla_poo.inactivar():
            return (False, "La malla curricular no puede deshabilitarse desde su estado actual")

    else:
        return (False, "No válido")

    malla_db.estado = malla_poo.estado.value
    malla_db.save(update_fields=["estado"])
    return (True, "El estado de la malla curricular ha sido actualizado correctamente.")

def servicio_clonar_malla_curricular(id_malla_curricular_bd, nueva_version_de_malla, nuevo_nombre=None):
    from academico.models import UnidadCurricular

    malla_curricular_db = MallaCurricular.objects.get(id=id_malla_curricular_bd)

    malla_poo = _construir_malla_poo(malla_curricular_db, cargar_unidades=True)

    nuevo_codigo = generar_identificador_siguiente(MallaCurricular, "MC", "codigo_de_malla")
    clon_poo = malla_poo.clonar(nuevo_codigo, str(nueva_version_de_malla).strip())

    if nuevo_nombre and str(nuevo_nombre).strip():
        clon_poo.nombre = str(nuevo_nombre).strip()

    with transaction.atomic():
        nueva_malla_curricular_db = MallaCurricular.objects.create(
            carrera=malla_curricular_db.carrera,
            codigo_de_malla=clon_poo.codigo_de_malla,
            nombre=clon_poo.nombre,
            area_de_conocimiento=clon_poo.area_de_conocimiento,
            duracion_semanas=clon_poo.duracion_semanas,
            version_de_malla=clon_poo.version_de_malla,
            modalidad=clon_poo.modalidad.value,
            estado=clon_poo.estado.value,
            total_horas_nivelacion=clon_poo.total_horas_nivelacion,
        )

        for unidad_poo in clon_poo.obtener_unidades_curriculares():
            UnidadCurricular.objects.create(
                malla_curricular=nueva_malla_curricular_db,
                codigo_de_unidad=generar_identificador_siguente(
                    UnidadCurricular, "UC", "codigo_de_unidad"
                ),
                nombre=unidad_poo.nombre,
                area_de_conocimiento=unidad_poo.area_de_conocimiento,
                horas_totales=unidad_poo.horas_totales,
                horas_semanales=unidad_poo.horas_semanales,
                horas_sincronicas=unidad_poo.horas_sincronicas,
                horas_asincronicas=unidad_poo.horas_asincronicas,
                tipo_de_componente=unidad_poo.tipo_de_componente.value,
                criterio_de_aprobacion=unidad_poo.criterio_de_aprobacion,
                porcentaje_minimo_asistencia=unidad_poo.porcentaje_minimo_asistencia,
            )

    return nueva_malla_curricular_db
