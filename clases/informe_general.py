from datetime import date

#Enums
from clases.enums.tipo_de_informe import TipoDeInforme
from clases.enums.estado_de_informe import EstadoDeInforme
from clases.enums.estado_de_periodo import EstadoDePeriodo
from clases.enums.estado_de_aprobacion import EstadoDeAprobacion
from clases.enums.estado_de_matricula import EstadoDeMatricula

#Interface
from clases.interfaces.i_informe_institucional import IInformeInstitucional

from clases.periodo_de_nivelacion import PeriodoDeNivelacion
from clases.cohorte_de_matricula import CohorteDeMatricula


class InformeGeneral(IInformeInstitucional): #Interfaz
    def __init__(self, codigo_de_informe, periodo_academico: PeriodoDeNivelacion, tipo_de_informe: TipoDeInforme):
        self.codigo_de_informe = codigo_de_informe
        self.periodo_academico = periodo_academico
        self.tipo_de_informe = tipo_de_informe #Instancia
        self._estado_de_informe = EstadoDeInforme.BORRADOR
        self._cohortes = [] # Lista de instancias CohorteDeMatricula
        self._fecha_de_emision  = None #datetime.date


    def agregar_cohorte_de_matricula(self, cohorte_de_matricula: CohorteDeMatricula):
        if not isinstance(cohorte_de_matricula, CohorteDeMatricula):
            return False
            
        if cohorte_de_matricula in self._cohortes:
            return False
            
        self._cohortes.append(cohorte_de_matricula)
        return True


    def emitir_informe_de_nivelacion(self):
        if self.periodo_academico._estado != EstadoDePeriodo.CERRADO:
            return False
        total_matriculados = self.obtener_total_matriculados()
        self._fecha_de_emision  = date.today()
        self._estado_de_informe = EstadoDeInforme.REVISION
        return True
       
    
    def obtener_total_matriculados(self):
        total_matriculados = 0
        for cohorte in self._cohortes:
            total_matriculados += cohorte.calcular_total_matriculados()
            
        return total_matriculados
    
    
    def consolidar_estadisticas_institucionales(self, evaluaciones_del_periodo: list) -> dict:
        consolidado_de_estadisticas = {}
        for cohorte in self._cohortes:
            nombre_carrera = cohorte.carrera_registrada.nombre
            
            if nombre_carrera not in consolidado_de_estadisticas:
                consolidado_de_estadisticas[nombre_carrera] = {"Número de aprobados": 0, "Número de reprobados": 0, "Número de retirados": 0, "Número de anulados": 0, "Número de segunda matricula": 0}

            estadisticas_de_registro = cohorte.obtener_estadisticas_de_registro()
            consolidado_de_estadisticas[nombre_carrera]["Número de segunda matricula"] += estadisticas_de_registro.get("Total segunda matricula", 0)

        for evaluacion in evaluaciones_del_periodo:
            carrera_estudiante = evaluacion.estudiante.carrera_registrada.nombre
            if carrera_estudiante in consolidado_de_estadisticas:
                estado = evaluacion._estado_de_aprobacion
                
                if estado == EstadoDeAprobacion.APROBADO:
                    consolidado_de_estadisticas[carrera_estudiante]["Número de aprobados"] += 1
                elif estado == EstadoDeAprobacion.REPROBADO:
                    consolidado_de_estadisticas[carrera_estudiante]["Número de reprobados"] += 1
                elif estado == EstadoDeAprobacion.RETIRADO:
                    consolidado_de_estadisticas[carrera_estudiante]["Número de retirados"] += 1
                elif estado == EstadoDeAprobacion.ANULADO:
                    consolidado_de_estadisticas[carrera_estudiante]["Número de anulados"] += 1

        return consolidado_de_estadisticas
            
            
    def procesar_retiros_y_anulaciones(self):
        retiros = 0
        anulaciones = 0
        for cohorte in self._cohortes:
            for estudiante in cohorte._estudiantes_matriculados:
                if estudiante._estado_de_matricula == EstadoDeMatricula.RETIRADO:
                    retiros += 1
                elif estudiante._estado_de_matricula == EstadoDeMatricula.ANULADO:
                    anulaciones += 1
        return {"Retiros": retiros, "Anulaciones": anulaciones}


    def estimar_tasas_de_aprobacion(self, evaluaciones_del_periodo: list):
        total_de_evaluaciones = len(evaluaciones_del_periodo)
        if total_de_evaluaciones == 0:
            return {"Tasa de aprobación": "0%", "Tasa de reprobación": "0%", "Tasa de retiros": "0%"}

        aprobados = 0
        reprobados = 0
        retiros = 0

        for evaluacion in evaluaciones_del_periodo:
            estado = evaluacion._estado_de_aprobacion
            
            if estado == EstadoDeAprobacion.APROBADO:
                aprobados += 1
            elif estado == EstadoDeAprobacion.REPROBADO:
                reprobados += 1
            elif estado in (EstadoDeAprobacion.RETIRADO, EstadoDeAprobacion.ANULADO):
                retiros += 1

        tasa_de_aprobacion = (aprobados / total_de_evaluaciones) * 100
        tasa_de_reprobacion = (reprobados / total_de_evaluaciones) * 100
        tasa_de_retiros = (retiros / total_de_evaluaciones) * 100

        return {
            "Tasa de aprobación": f"{round(tasa_de_aprobacion, 2)}%",
            "Tasa de reprobación": f"{round(tasa_de_reprobacion, 2)}%",
            "Tasa de retiros": f"{round(tasa_de_retiros, 2)}%",
        }