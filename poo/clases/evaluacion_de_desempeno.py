from poo.clases.usuarios.docente import Docente

from poo.clases.interfaces.i_estrategia_de_evaluacion import IEstrategiaDeEvaluacion


class EvaluacionDeDesempeno:
    def __init__(self, docente_responsable: Docente, porcentaje_de_horas_cumplidas: float, entrega_oportuna_de_calificaciones: bool, porcentaje_de_aprobacion_paralelo: float, resultado_de_evaluacion_estudiantil: float):
        self.docente_responsable = docente_responsable # Instancia de Docente
        self.porcentaje_de_horas_cumplidas = porcentaje_de_horas_cumplidas
        self.entrega_oportuna_de_calificaciones = entrega_oportuna_de_calificaciones
        self.porcentaje_de_aprobacion_paralelo = porcentaje_de_aprobacion_paralelo
        self.resultado_de_evaluacion_estudiantil = resultado_de_evaluacion_estudiantil
        self._puntaje_final = 0.0
        
        
    def procesar_evaluacion(self, estrategia: IEstrategiaDeEvaluacion):
        self._puntaje_final = estrategia.calcular_ponderacion(
            self.porcentaje_de_horas_cumplidas,
            self.entrega_oportuna_de_calificaciones,
            self.porcentaje_de_aprobacion_paralelo,
            self.resultado_de_evaluacion_estudiantil
        )
        return self._puntaje_final


    def obtener_resumen_de_desempeno(self):
        entrega_calificaciones = "Sí"
        if not self.entrega_oportuna_de_calificaciones:
            entrega_calificaciones = "No"

        return {
            "Docente responsable": f"{self.docente_responsable.nombres} {self.docente_responsable.apellidos}",
            "Cumplimiento de carga horaria": f"{self.porcentaje_de_horas_cumplidas}%",
            "Entrega oportuna de calificaciones": entrega_calificaciones,
            "Aprobación del paralelo": f"{self.porcentaje_de_aprobacion_paralelo}%",
            "Evaluación estudiantil": f"{self.resultado_de_evaluacion_estudiantil}/100.0",
            "Ponderación de desempeño final": self._puntaje_final
        }