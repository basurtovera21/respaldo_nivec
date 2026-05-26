from datetime import date

from clases.enums.dia_de_semana import DiaDeSemana
from clases.enums.estado_de_aprobacion import EstadoDeAprobacion
from clases.enums.estado_de_cohorte import EstadoDeCohorte
from clases.enums.estado_de_informe import EstadoDeInforme
from clases.enums.estado_de_malla import EstadoDeMalla
from clases.enums.estado_de_matricula import EstadoDeMatricula
from clases.enums.estado_de_periodo import EstadoDePeriodo
from clases.enums.estado_de_usuario import EstadoDeUsuario
from clases.enums.estado_de_vinculacion import EstadoDeVinculacion
from clases.enums.formato_de_exportacion import FormatoDeExportacion
from clases.enums.jornada import Jornada
from clases.enums.modalidad import Modalidad
from clases.enums.perfil_administrativo import PerfilAdministrativo
from clases.enums.registro_de_cupo import RegistroDeCupo
from clases.enums.tiempo_de_dedicacion import TiempoDeDedicacion
from clases.enums.tipo_de_cohorte import TipoDeCohorte
from clases.enums.tipo_de_componente import TipoDeComponente
from clases.enums.tipo_de_identificacion import TipoDeIdentificacion
from clases.enums.tipo_de_informe import TipoDeInforme
from clases.enums.tipo_de_sesion import TipoDeSesion
from clases.enums.tipo_de_vinculacion import TipoDeVinculacion


from clases.universidad import Universidad
from clases.campus import Campus
from clases.carrera import Carrera


from clases.usuarios.coordinador_dan import CoordinadorDAN
from clases.usuarios.coordinador_unidad_academica import CoordinadorUnidadAcademica
from clases.usuarios.docente import Docente
from clases.usuarios.estudiante import Estudiante


from clases.unidad_curricular import UnidadCurricular
from clases.malla_curricular import MallaCurricular
from clases.periodo_de_nivelacion import PeriodoDeNivelacion
from clases.paralelo import Paralelo
from clases.horario import Horario


from clases.consolidado_academico import ConsolidadoAcademico
from clases.cohorte_de_matricula import CohorteDeMatricula
from clases.evaluacion_academica import EvaluacionAcademica


from clases.informe_general import InformeGeneral

#Prueba de clases base: Universidad, Campus, Carrera.
def probar_clases_base():
    universidad = Universidad(
        nombre = "Universidad Laica Eloy Alfaro de Manabí",
        abreviatura = "ULEAM",
        codigo_sniese = "-",
        direccion_matriz = "-",
        identificador_visual = "-"
    )
    print(f"UNIVERSIDAD: {universidad.nombre} ({universidad.abreviatura})")
    print()

    campus = Campus(
        codigo_de_campus = "-",
        nombre = "Central, Manta",
        direccion_fisica = "-",
        provincia = "Manabí",
        infraestructura_compartida = False
    )
    print(f"CAMPUS: {campus.nombre}. Infraestructura compartida: {campus.infraestructura_compartida}")
    print()

    carrera_activa = Carrera(
        codigo_de_carrera = "-001",
        nombre = "Software",
        modalidad = Modalidad.PRESENCIAL,
        campo_de_conocimiento = "-",
        vigencia_sniese = date(2028, 12, 31)
    )
    carrera_inactiva = Carrera(
        codigo_de_carrera = "-002",
        nombre = "Ingeniería Civil",
        modalidad = Modalidad.PRESENCIAL,
        campo_de_conocimiento = "-",
        vigencia_sniese = date(2020, 6, 30)
    )
    print("CARRERA:")
    print(f"Carrera activa ({carrera_activa.nombre}): {carrera_activa.esta_activa()}")
    print(f"Carrera inactiva ({carrera_inactiva.nombre}): {carrera_inactiva.esta_activa()}")
    print()


#Prueba de instanciación de usuarios
def probar_instanciacion_usuarios():
    datos_base = dict(
        tipo_de_identificacion = TipoDeIdentificacion.CEDULA,
        identificacion = "1316719804",
        nombres = "Carlos Eduardo",
        apellidos = "Basurto Vera",
        correo_institucional = "e1316719804@uleam.edu.ec",
        contrasena = "123456789",
        fecha_de_nacimiento = date(2004, 5, 4),
        sexo = "Masculino",
        etnia = "Mestizo",
        porcentaje_de_discapacidad = 0.0,
        celular = "0995621013",
        direccion = "Manta, Manabí"
    )

    coordinador_dan = CoordinadorDAN(
        **datos_base,
        identificador_administrativo = "ADM-001",
        perfil_administrativo = PerfilAdministrativo.DIRECTOR_DAN,
        identificador_coordinador_dan = "DAN-001"
    )
    print("COORDINADOR DAN")
    print(f"{coordinador_dan.nombres} {coordinador_dan.apellidos}. Perfil: {coordinador_dan.perfil_administrativo.value}")
    print()

    docente = Docente(
        **{**datos_base,
           "identificacion": "1300000000",
           "nombres": "Dengy Rodolfo", "apellidos": "Macías Mera",
           "correo_institucional": "e1300000000@uleam.edu.ec"},
        identificador_institucional = "DOC-001",
        tipo_de_vinculacion = TipoDeVinculacion.CONTRATO,
        tiempo_de_dedicacion = TiempoDeDedicacion.TIEMPO_COMPLETO,
        carga_horaria_maxima = 40.0
    )
    print("DOCENTE")
    print(f"{docente.nombres} {docente.apellidos}")
    print(f"Vinculación: {docente.tipo_de_vinculacion.value}")
    print(f"Estado de vinculación: {docente._estado_de_vinculacion.value}")
    print(f"Carga actual: {docente._carga_horaria_actual}/{docente.carga_horaria_maxima} horas")
    print()

    carrera_ti = Carrera(
        codigo_de_carrera = "-003",
        nombre = "Ingeniería en Tecnologías de la Información",
        modalidad = Modalidad.PRESENCIAL,
        campo_de_conocimiento = "-",
        vigencia_sniese = date(2028, 12, 31)
    )
    campus_chone = Campus(
        codigo_de_campus = "-",
        nombre = "Extensión Chone",
        direccion_fisica = "-",
        provincia = "Manabí",
        infraestructura_compartida = False
    )
    estudiante = Estudiante(
        **{**datos_base,
           "identificacion": "1300000001",
           "nombres": "Luís Angel", "apellidos": "Del Mónaco Palma",
           "correo_institucional": "e1300000001@uleam.edu.ec"},
        identificador_institucional = "EST-001",
        numero_de_matricula = "MAT-2026-001",
        jornada = Jornada.MATUTINA,
        registro_de_cupo = RegistroDeCupo.REGULAR,
        carrera_registrada = carrera_ti,
        campus_registrado = campus_chone,
        estado_de_matricula = EstadoDeMatricula.ASPIRANTE
    )
    print(f"ESTUDIANTE: {estudiante.nombres} {estudiante.apellidos}")
    print(f"CARRERA: {estudiante.carrera_registrada.nombre}")
    print(f"Estado de matrícula: {estudiante._estado_de_matricula.value}")
    print()

    coordinador_ua = CoordinadorUnidadAcademica(
        **{**datos_base,
           "identificacion": "1300000002",
           "nombres": "Anthony José", "apellidos": "Sanchez Peraza",
           "correo_institucional": "e1300000002@uleam.edu.ec"},
        identificador_administrativo = "ADM-002",
        perfil_administrativo = PerfilAdministrativo.COORDINADOR_UA,
        identificador_institucional = "DOC-002",
        tipo_de_vinculacion = TipoDeVinculacion.NOMBRAMIENTO,
        tiempo_de_dedicacion = TiempoDeDedicacion.TIEMPO_COMPLETO,
        carga_horaria_maxima = 40.0,
        identificador_coordinador_ua = "CUA-001",
        unidad_academica = "Facultad de Ciencias de la Vida y Tecnologías"
    )
    print(f"COORDINADOR UA: {coordinador_ua.nombres} {coordinador_ua.apellidos}")
    print(f"Unidad académica: {coordinador_ua.unidad_academica}")
    print(f"MRO: {CoordinadorUnidadAcademica.__mro__}")
    print()

#Probar estructura academíca: UnidadCurricular, MallaCurricular, PeriodoDeNivelacion, Paralelo y Horario 
def probar_estructura_academica():
    unidad = UnidadCurricular(
        codigo_de_unidad = "IS-303",
        nombre = "Programación Orientada a Objetos",
        area_de_conocimiento = ["Ingeniería de Software", "Desarrollo de Software"],
        horas_totales = 144.0,
        horas_semanales = 6.0,
        horas_sincronicas = 96.0,
        horas_asincronicas = 48.0,
        tipo_de_componente = TipoDeComponente.TEORICO,
        criterio_de_aprobacion = 7.0,
        porcentaje_minimo_asistencia = 70.0
    )
    print(f"UNIDAD CURRICULAR: {unidad.nombre}")
    print(f"Distribución de horas válida: {unidad.validar_distribucion_de_horas_totales()}")
    print()

    unidad_invalida = UnidadCurricular(
        codigo_de_unidad = "IS-104",
        nombre = "Álgebra Lineal",
        area_de_conocimiento = ["Matemáticas"],
        horas_totales = 144.0,
        horas_semanales = 4.0,
        horas_sincronicas = 86.0,
        horas_asincronicas = 48.0,
        tipo_de_componente = TipoDeComponente.TEORICO
    )
    print(f"Distribución de horas válida: {unidad_invalida.validar_distribucion_de_horas_totales()}")
    print()

    periodo = PeriodoDeNivelacion(
        codigo_periodo = "PER-2026-1",
        anio = 2026,
        periodo = "2026-1",
        fecha_inicio = date(2026, 4, 1),
        fecha_fin = date(2026, 8, 1),
        modalidad = Modalidad.PRESENCIAL,
        numero_periodo = 1
    )
    print("PERIODO DE NIVELACIÓN")
    print(f"Periodo: {periodo.periodo}")
    print(f"Estado: {periodo._estado.value}")
    print(f"Duración: {periodo.calcular_duracion_semanas()} semanas")
    print()

    paralelo = Paralelo(
        codigo_de_paralelo = "PAR-001",
        nombre = "Paralelo A",
        jornada = Jornada.MATUTINA,
        modalidad = Modalidad.PRESENCIAL,
        capacidad_maxima = 35
    )
    print(f"PARALELO: {paralelo.nombre}")
    print(f"Tiene cupo disponible: {paralelo.tiene_cupo_disponible()}")
    print(f"Estudiantes: {len(paralelo._estudiantes_matriculados)}/{paralelo.capacidad_maxima}")
    print()

    from datetime import time
    horario_1 = Horario(
        dia_semana = DiaDeSemana.LUNES,
        hora_inicio = time(8, 0),
        hora_fin = time(10, 0),
        espacio_de_imparticion = "Aula virtual",
        modalidad = Modalidad.PRESENCIAL,
        numero_semana = 1,
        tipo_de_sesion = TipoDeSesion.SINCRONICA,
        docente_responsable = None
    )
    horario_2 = Horario(
        dia_semana = DiaDeSemana.LUNES,
        hora_inicio = time(9, 0),
        hora_fin = time(11, 0),
        espacio_de_imparticion = "Aula virtual",
        modalidad = Modalidad.PRESENCIAL,
        numero_semana = 1,
        tipo_de_sesion = TipoDeSesion.SINCRONICA,
        docente_responsable = None
    )
    horario_3 = Horario(
        dia_semana = DiaDeSemana.MARTES,
        hora_inicio = time(8, 0),
        hora_fin = time(10, 0),
        espacio_de_imparticion = "Aula virtual",
        modalidad = Modalidad.PRESENCIAL,
        numero_semana = 1,
        tipo_de_sesion = TipoDeSesion.SINCRONICA,
        docente_responsable = None
    )
    print("HORARIO")
    print(f"horario_1 (lunes 08:00-10:00). Duración: {horario_1.determinar_duracion_horas()} hora(s)")
    print(f"Conflicto con horario_2 (lunes 09:00-11:00): {horario_1.verificar_conflicto_horario(horario_2)}")
    print(f"Conflicto con horario_3 (martes 08:00-10:00): {horario_1.verificar_conflicto_horario(horario_3)}")
    print()

#Prueba de procesos académicos
def probar_procesos_academicos():
    periodo_de_nivelacion = PeriodoDeNivelacion(
        codigo_periodo = "PER-2026-1",
        anio = 2026,
        periodo = "2026-1",
        fecha_inicio = date(2026, 4, 1),
        fecha_fin = date(2026, 8, 1),
        modalidad = Modalidad.PRESENCIAL,
        numero_periodo = 1
    )

    consolidado_academico = ConsolidadoAcademico(
        periodo_academico = periodo_de_nivelacion,
        fecha_de_corte = date(2026, 7, 15),
        total_de_cupos_aceptados = 320
    )
    print(f"CONSOLIDADO ACADÉMICO: {consolidado_academico.periodo_academico.periodo}")
    print(f"Cupos aceptados: {consolidado_academico.total_de_cupos_aceptados}")
    print(f"Registros totales: {consolidado_academico._registros_totales}")
    print(f"Registros válidos: {consolidado_academico._registros_validos}")
    print(f"Registros observados: {consolidado_academico._registros_observados}")
    print()

    cohorte = CohorteDeMatricula(
        codigo_de_registro = "COH-2026-1-A",
        fecha_de_cierre = date(2026, 4, 14),
        periodo_de_nivelacion = periodo_de_nivelacion,
        tipo_de_cohorte = TipoDeCohorte.PRIMERA_MATRICULA
    )
    print(f"COHORTE DE MATRÍCULA: {cohorte.codigo_de_registro}")
    print(f"Tipo: {cohorte.tipo_de_cohorte.value}")
    print(f"Estado: {cohorte._estado_de_cohorte.value}")
    print(f"Total matriculados: {cohorte.calcular_total_matriculados()}")
    print()

    unidad_curricular = UnidadCurricular(
        codigo_de_unidad = "IS-204",
        nombre = "Matemática Discreta",
        area_de_conocimiento = ["Matemática"],
        horas_totales = 144.0,
        horas_semanales = 6.0,
        horas_sincronicas = 96.0,
        horas_asincronicas = 48.0,
        tipo_de_componente = TipoDeComponente.TEORICO,
        criterio_de_aprobacion = 7.0,
        porcentaje_minimo_asistencia = 70.0
    )
    
    datos_base = dict(
        tipo_de_identificacion = TipoDeIdentificacion.CEDULA,
        identificacion = "1300000003",
        nombres = "Vinicio Alejandro",
        apellidos = "Velasteguí Solorzano",
        correo_institucional = "e1300000003@uleam.edu.ec",
        contrasena = "123456789",
        fecha_de_nacimiento = date(2004, 1, 1),
        sexo = "Masculino",
        etnia = "Mestizo",
        porcentaje_de_discapacidad = 0.0,
        celular = "0999999999",
        direccion = "Manta, Manabí"
    )
    carrera = Carrera(
        codigo_de_carrera = "CAR-001",
        nombre = "Software",
        modalidad = Modalidad.PRESENCIAL,
        campo_de_conocimiento = "-",
        vigencia_sniese = date(2028, 12, 31)
    )
    campus = Campus(
        codigo_de_campus = "CAM-001",
        nombre = "Campus Central",
        direccion_fisica = "-",
        provincia = "Manabí",
        infraestructura_compartida = False
    )
    estudiante = Estudiante(
        **datos_base,
        identificador_institucional = "EST-010",
        numero_de_matricula = "MAT-2025-010",
        jornada = Jornada.MATUTINA,
        registro_de_cupo = RegistroDeCupo.REGULAR,
        carrera_registrada = carrera,
        campus_registrado = campus,
        estado_de_matricula = EstadoDeMatricula.MATRICULADO
    )
    evaluacion = EvaluacionAcademica(
        estudiante = estudiante,
        unidad_curricular = unidad_curricular
    )
    print(f"EVALUACIÓN ACADÉMICA: {evaluacion.estudiante.nombres} {evaluacion.estudiante.apellidos} ({evaluacion.unidad_curricular.nombre})")
    print(f"Parcial 1: {evaluacion._calificacion_parcial_1}")
    print(f"Parcial 2: {evaluacion._calificacion_parcial_2}")
    print(f"Nota final: {evaluacion._nota_final}")
    print(f"Asistencia: {evaluacion._porcentaje_asistencia}%")
    print(f"Estado: {evaluacion._estado_de_aprobacion.value}")
    print()

#Prueba de InformeGeneral
def probar_informe_general():
    periodo_de_nivelacion = PeriodoDeNivelacion(
        codigo_periodo = "PER-2026-1",
        anio = 2026,
        periodo = "2026-1",
        fecha_inicio = date(2026, 4, 1),
        fecha_fin = date(2026, 8, 1),
        modalidad = Modalidad.PRESENCIAL,
        numero_periodo = 1
    )
    
    informe = InformeGeneral(
        codigo_de_informe = "INF-2025-1-ULEAM",
        periodo_academico = periodo_de_nivelacion,
        tipo_de_informe = TipoDeInforme.FINAL
    )
    
    print(f"INFORME: {informe.codigo_de_informe}")
    print(f"Tipo: {informe.tipo_de_informe.value}")
    print(f"Estado: {informe._estado_de_informe.value}")
    print(f"Fecha emisión: {informe._fecha_de_emision}")
    print(f"Cohortes registradas: {len(informe._cohortes)}")
    print()

#Prueba de sobreescritura
def probar_sobreescritura():
    print("SOBREESCRITURA")
    print()
    datos = dict(
        tipo_de_identificacion     = TipoDeIdentificacion.CEDULA,
        identificacion             = "1300000099",
        nombres                    = "Carlos Eduardo",
        apellidos                  = "Basurto Vera",
        correo_institucional       = "e1300000099@uleam.edu.ec",
        contrasena                 = "123456789",
        fecha_de_nacimiento        = date(2004, 5, 4),
        sexo                       = "Masculino",
        etnia                      = "Mestizo",
        porcentaje_de_discapacidad = 0.0,
        celular                    = "0990000000",
        direccion                  = "Manta, Manabí"
    )
    carrera = Carrera("-", "Software", Modalidad.PRESENCIAL, "-", date(2028,12,31))
    campus  = Campus("-", "Central, Manta", "-", "Manabí", False)

    docente = Docente(
        **{**datos, "identificacion": "1300000010"},
        identificador_institucional = "DOC-099",
        tipo_de_vinculacion         = TipoDeVinculacion.CONTRATO,
        tiempo_de_dedicacion        = TiempoDeDedicacion.TIEMPO_COMPLETO,
        carga_horaria_maxima        = 40.0
    )
    docente.iniciar_sesion() #Docente

    estudiante = Estudiante(
        **{**datos, "identificacion": "1300000011"},
        identificador_institucional = "EST-099",
        numero_de_matricula         = "MAT-099",
        jornada                     = Jornada.MATUTINA,
        registro_de_cupo            = RegistroDeCupo.REGULAR,
        carrera_registrada          = carrera,
        campus_registrado           = campus,
        estado_de_matricula         = EstadoDeMatricula.MATRICULADO
    )
    estudiante.iniciar_sesion() #Estudiante

    coordinador_dan = CoordinadorDAN(
        **{**datos, "identificacion": "1300000012"},
        identificador_administrativo  = "ADM-099",
        perfil_administrativo         = PerfilAdministrativo.DIRECTOR_DAN,
        identificador_coordinador_dan = "DAN-099"
    )
    coordinador_dan.iniciar_sesion() #Coodinador DAN

    coordinador_ua = CoordinadorUnidadAcademica(
        **{**datos, "identificacion": "1300000013"},
        identificador_administrativo = "ADM-098",
        perfil_administrativo        = PerfilAdministrativo.COORDINADOR_UA,
        identificador_institucional  = "DOC-099",
        tipo_de_vinculacion          = TipoDeVinculacion.NOMBRAMIENTO,
        tiempo_de_dedicacion         = TiempoDeDedicacion.TIEMPO_COMPLETO,
        carga_horaria_maxima         = 40.0,
        identificador_coordinador_ua = "CUA-099",
        unidad_academica             = "Facultad de Ciencias Informáticas"
    )
    coordinador_ua.iniciar_sesion() #Coordinar UA
    print()

#Prueba de sobrecarga
def probar_sobrecarga():
    print("SOBRECARGA")
    print()
    #MallaCurricular (agregar_unidad_curricular() con *args)
    malla = MallaCurricular(
        codigo_de_malla      = "MALLA-001",
        nombre               = "Malla Nivelación 2026",
        area_de_conocimiento = "-",
        duracion_semanas     = 16,
        version_de_malla     = "v1",
        modalidad            = Modalidad.PRESENCIAL
    )
    unidad_1 = UnidadCurricular("UC-001", "Matemática Discreta", ["Matemática"], 80.0, 8.0, 60.0, 20.0, TipoDeComponente.TEORICO)
    unidad_2 = UnidadCurricular("UC-002", "Álgebra Lineal", ["Matemática"], 80.0, 8.0, 60.0, 20.0, TipoDeComponente.TEORICO)
    unidad_3 = UnidadCurricular("UC-003", "Programación Orientada a Objetos", ["Software"], 96.0, 6.0, 64.0, 32.0, TipoDeComponente.TEORICO)

    print("Agregar una unidad:")
    malla.agregar_unidad_curricular(unidad_1)

    print("Agregar dos unidades a la vez:")
    malla.agregar_unidad_curricular(unidad_2, unidad_3)

    print("Intento de agregar un duplicado de unidad:")
    malla.agregar_unidad_curricular(unidad_1)

    print(f"Total horas de nivelación: {malla._total_horas_nivelacion} horas")
    print(f"Unidades registradas: {len(malla._unidades_curriculares)}")
    print()

    #Evaluación académica (registrar_calificacion() con *args e isinstance)
    datos = dict(
        tipo_de_identificacion     = TipoDeIdentificacion.CEDULA,
        identificacion             = "1300000020",
        nombres                    = "Luís Angel",
        apellidos                  = "Del Mónaco Palma",
        correo_institucional       = "e1300000020@uleam.edu.ec",
        contrasena                 = "123456789",
        fecha_de_nacimiento        = date(2006, 1, 1),
        sexo                       = "Masculino",
        etnia                      = "Mestizo",
        porcentaje_de_discapacidad = 0.0,
        celular                    = "0981111111",
        direccion                  = "Manta"
    )
    carrera = Carrera("-", "Software", Modalidad.PRESENCIAL, "-", date(2028,12,31))
    campus  = Campus("-", "Central, Manta", "-", "Manabí", False)
    estudiante = Estudiante(
        **datos,
        identificador_institucional = "EST-020",
        numero_de_matricula         = "MAT-020",
        jornada                     = Jornada.MATUTINA,
        registro_de_cupo            = RegistroDeCupo.REGULAR,
        carrera_registrada          = carrera,
        campus_registrado           = campus,
        estado_de_matricula         = EstadoDeMatricula.MATRICULADO
    )
    evaluacion = EvaluacionAcademica(estudiante = estudiante, unidad_curricular = unidad_1)

    print("Parcial específico (int, float):")
    evaluacion.registrar_calificacion(1, 8.5)
    evaluacion.registrar_calificacion(2, 7.0)
    print()

    print("Ambos parciales directos (float, float):")
    evaluacion2 = EvaluacionAcademica(estudiante = estudiante, unidad_curricular = unidad_2)
    evaluacion2.registrar_calificacion(9.0, 6.5)
    print()

    print("Calcular nota final y verificar aprobación:")
    evaluacion.calcular_nota_final()
    evaluacion.registrar_asistencia_final(85.0)
    evaluacion.verificar_aprobacion()
    print(f"Nota final: {evaluacion._nota_final}. Estado de aprobación: {evaluacion._estado_de_aprobacion.value}")
    print()

    print("Reprobado por porcentaje de asistencia:")
    evaluacion3 = EvaluacionAcademica(estudiante = estudiante, unidad_curricular = unidad_3)
    evaluacion3.registrar_calificacion(1, 9.0)
    evaluacion3.registrar_calificacion(2, 8.0)
    evaluacion3.calcular_nota_final()
    evaluacion3.registrar_asistencia_final(50.0)
    evaluacion3.verificar_aprobacion()
    print(f"Nota final: {evaluacion3._nota_final}. Estado de aprobación: {evaluacion3._estado_de_aprobacion.value}")
    print()

#Prueba de interfaz
def probar_interfaz():
    periodo = PeriodoDeNivelacion(
        codigo_periodo = "PER-2026-1",
        anio           = 2026,
        periodo        = "2026-1",
        fecha_inicio   = date(2026, 4, 1),
        fecha_fin      = date(2026, 8, 1),
        modalidad      = Modalidad.PRESENCIAL,
        numero_periodo = 1
    )
    # Estado CERRADO para poder emitir el informe
    periodo._estado = EstadoDePeriodo.CERRADO

    cohorte = CohorteDeMatricula(
        codigo_de_registro    = "COH-2026-1-A",
        fecha_de_cierre       = date(2026, 4, 14),
        periodo_de_nivelacion = periodo,
        tipo_de_cohorte       = TipoDeCohorte.PRIMERA_MATRICULA
    )
    #120 matriculados
    cohorte._total_primera_matricula = 120

    informe = InformeGeneral(
        codigo_de_informe = "INF-2026-1-ULEAM",
        periodo_academico = periodo,
        tipo_de_informe   = TipoDeInforme.FINAL
    )
    informe._cohortes.append(cohorte)

    informe.emitir_informe_de_nivelacion()
    print()
    informe.exportar_consolidado_de_estudiantes(FormatoDeExportacion.PDF)
    print()
    informe.exportar_consolidado_de_estudiantes(FormatoDeExportacion.EXCEL)
    print()

def main():
    print("Verificación inicial de sistema")
    print()
    probar_clases_base()
    probar_instanciacion_usuarios()
    probar_estructura_academica()
    probar_procesos_academicos()
    probar_informe_general()
    probar_sobreescritura()
    probar_sobrecarga()
    probar_interfaz()   

if __name__ == "__main__":
    main()