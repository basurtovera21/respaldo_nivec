from poo.clases.interfaces.i_estrategia_de_evaluacion import IEstrategiaDeEvaluacion


class EvaluacionDeDesempeno:
    """
    Calcula el puntaje de desempeño de un docente usando el patrón Strategy.

    Atributos evaluados:
        - porcentaje_de_horas_cumplidas (0-100)
        - entrega_oportuna_de_calificaciones (bool)
        - porcentaje_de_aprobacion_paralelo (0-100)
        - resultado_de_evaluacion_estudiantil (0-100)

    Uso desde Django (v_procesos_academicos.py):
        evaluacion_poo = EvaluacionDeDesempeno(...)
        puntaje = evaluacion_poo.procesar_evaluacion(estrategia)
    """

    def __init__(self, docente_responsable, porcentaje_de_horas_cumplidas: float,
                 entrega_oportuna_de_calificaciones: bool,
                 porcentaje_de_aprobacion_paralelo: float,
                 resultado_de_evaluacion_estudiantil: float):
        self._docente_responsable = docente_responsable
        self._porcentaje_de_horas_cumplidas = porcentaje_de_horas_cumplidas
        self._entrega_oportuna_de_calificaciones = entrega_oportuna_de_calificaciones
        self._porcentaje_de_aprobacion_paralelo = porcentaje_de_aprobacion_paralelo
        self._resultado_de_evaluacion_estudiantil = resultado_de_evaluacion_estudiantil
        self._puntaje_final = 0.0

    @property
    def docente_responsable(self):
        return self._docente_responsable

    @property
    def porcentaje_de_horas_cumplidas(self):
        return self._porcentaje_de_horas_cumplidas

    @property
    def entrega_oportuna_de_calificaciones(self):
        return self._entrega_oportuna_de_calificaciones

    @property
    def porcentaje_de_aprobacion_paralelo(self):
        return self._porcentaje_de_aprobacion_paralelo

    @property
    def resultado_de_evaluacion_estudiantil(self):
        return self._resultado_de_evaluacion_estudiantil

    @property
    def puntaje_final(self):
        return self._puntaje_final

    def procesar_evaluacion(self, estrategia: IEstrategiaDeEvaluacion) -> float:
        """Calcula el puntaje final delegando al Strategy configurado."""
        self._puntaje_final = estrategia.calcular_ponderacion(
            self._porcentaje_de_horas_cumplidas,
            self._entrega_oportuna_de_calificaciones,
            self._porcentaje_de_aprobacion_paralelo,
            self._resultado_de_evaluacion_estudiantil
        )
        return self._puntaje_final

    def obtener_resumen_de_desempeno(self) -> dict:
        return {
            "Cumplimiento de carga horaria": f"{self._porcentaje_de_horas_cumplidas}%",
            "Entrega oportuna de calificaciones": "Sí" if self._entrega_oportuna_de_calificaciones else "No",
            "Aprobación del paralelo": f"{self._porcentaje_de_aprobacion_paralelo}%",
            "Evaluación estudiantil": f"{self._resultado_de_evaluacion_estudiantil}/100.0",
            "Puntaje final": self._puntaje_final,
        }
