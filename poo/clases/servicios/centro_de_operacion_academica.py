#Patron de diseño estructural Facade

#Servicios internos
from poo.clases.servicios.distribuidor_de_estudiantes import DistribuidorDeEstudiantes
from poo.clases.servicios.procesador_de_informe import ProcesadorDeInforme

#Clases
from poo.clases.usuarios.estudiante import Estudiante
from poo.clases.usuarios.docente import Docente
from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion
from poo.clases.evaluacion_academica import EvaluacionAcademica
from poo.clases.informe_general import InformeGeneral
from poo.clases.cohorte_de_matricula import CohorteDeMatricula

#Enums
from poo.clases.enums.formato_de_exportacion import FormatoDeExportacion


class CentroDeOperacionAcademica:
#Simplifica el acceso a los subsistemas complejos de la capa POO.
#Subsistemas:
#-Estudiantes (matrícula, retiro, anulación)
#-Docentes (carga horaria, habilitación)
#-Distribución de estudiantes a paralelos
#-Registro y verificación de evaluaciones académicas
#-Emisión y exportación de informes institucionales
#-Control de periodos de nivelación
#-Administración de cohortes de matrícula


    def __init__(self):
        self._distribuidor = DistribuidorDeEstudiantes([])
        self._procesador = ProcesadorDeInforme()


    #Estudiantes
    def formalizar_matricula(self, estudiante: Estudiante):
        return estudiante.formalizar_matricula()

    def solicitar_retiro(self, estudiante: Estudiante):
        return estudiante.solicitar_retiro()

    def anular_matricula(self, estudiante: Estudiante):
        estudiante.anular_matricula()


    #Docentes
    def inhabilitar_docente(self, docente: Docente):
        docente.inhabilitar()

    def habilitar_docente(self, docente: Docente):
        docente.habilitar()

    def obtener_carga_academica(self, docente: Docente):
        return docente.visualizar_carga_academica()



    #Distribución de estudiantes
    def distribuir_estudiantes(self, paralelos: list, estudiantes: list):
        self._distribuidor.paralelos = paralelos
        return self._distribuidor.distribuir(estudiantes)


    #Registro y verificación de evaluaciones
    def registrar_evaluacion(self, evaluacion: EvaluacionAcademica, parcial_1: float, parcial_2: float, porcentaje_asistencia: float):
        evaluacion.registrar_calificacion(1, parcial_1)
        evaluacion.registrar_calificacion(2, parcial_2)
        evaluacion.registrar_asistencia_final(porcentaje_asistencia)
        evaluacion.calcular_nota_final()
        return evaluacion.verificar_aprobacion()

    def obtener_acta_de_paralelo(self, evaluaciones: list):
        return EvaluacionAcademica.registrar_evaluacion_de_paralelo(evaluaciones)


    #Control de periodos de nivelación
    def iniciar_periodo(self, periodo: PeriodoDeNivelacion):
        return periodo.iniciar_periodo_de_nivelacion()

    def finalizar_periodo(self, periodo: PeriodoDeNivelacion):
        return periodo.finalizar_periodo_de_nivelacion()

    def obtener_matriz_de_horarios(self, periodo: PeriodoDeNivelacion, paralelos: list):
        return periodo.generar_matriz_de_horarios(paralelos)


    #Administración de cohortes de matrícula
    def registrar_estudiante_en_cohorte(self, cohorte: CohorteDeMatricula, estudiante: Estudiante):
        return cohorte.registrar_estudiante_matriculado(estudiante)

    def obtener_estadisticas_de_cohorte(self, cohorte: CohorteDeMatricula):
        return cohorte.obtener_estadisticas_de_registro()


    #Emisión y exportación de informes
    def emitir_informe(self, informe: InformeGeneral):
        return informe.emitir_informe_de_nivelacion()

    def exportar_informe(self, informe: InformeGeneral, formato: FormatoDeExportacion):
        return self._procesador.exportar_consolidado(informe, formato)

    def consolidar_estadisticas(self, informe: InformeGeneral, evaluaciones: list):
        return informe.consolidar_estadisticas_institucionales(evaluaciones)

    def estimar_tasas(self, informe: InformeGeneral, evaluaciones: list):
        return informe.estimar_tasas_de_aprobacion(evaluaciones)