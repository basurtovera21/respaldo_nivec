"""
Implementación concreta del patrón Strategy para la evaluación de desempeño docente.

La estrategia estándar calcula un puntaje ponderado basado en 4 criterios:
    1. Porcentaje de horas cumplidas (peso configurable)
    2. Entrega oportuna de calificaciones (binario: suma o no)
    3. Porcentaje de aprobación del paralelo (peso configurable)
    4. Resultado de evaluación estudiantil (peso configurable)

Patrón Strategy:
    - IEstrategiaDeEvaluacion define el contrato
    - EstrategiaDeEvaluacionEstandar es la implementación concreta
    - Nuevas estrategias (ej: EstrategiaDeEvaluacionExigente) pueden crearse
      sin modificar esta clase ni la clase EvaluacionDeDesempeno

Principios:
    - OCP: Nuevas estrategias se crean como nuevas clases
    - LSP: Cualquier estrategia es intercambiable (misma interfaz)
    - SRP: Solo calcula la ponderación según sus pesos configurados
"""

from poo.clases.interfaces.i_estrategia_de_evaluacion import IEstrategiaDeEvaluacion


class EstrategiaDeEvaluacionEstandar(IEstrategiaDeEvaluacion):
    """
    Estrategia estándar de evaluación de desempeño docente.

    Calcula un puntaje ponderado donde cada criterio tiene un peso
    configurable (los pesos deben sumar 1.0 para un puntaje sobre 100).

    Ejemplo de configuración:
        estrategia = EstrategiaDeEvaluacionEstandar(
            porcentaje_horas=0.30,          # 30% del puntaje
            porcentaje_notas=0.20,          # 20% (binario: entregó o no)
            porcentaje_aprobacion=0.30,     # 30% del puntaje
            porcentaje_evaluacion_estudiantil=0.20  # 20% del puntaje
        )
    """

    def __init__(self, porcentaje_horas: float, porcentaje_notas: float,
                 porcentaje_aprobacion: float, porcentaje_evaluacion_estudiantil: float):
        """
        Args:
            porcentaje_horas: Peso del criterio de horas cumplidas (0.0 - 1.0)
            porcentaje_notas: Peso del criterio de entrega oportuna (0.0 - 1.0)
            porcentaje_aprobacion: Peso del criterio de aprobación (0.0 - 1.0)
            porcentaje_evaluacion_estudiantil: Peso de la evaluación estudiantil (0.0 - 1.0)
        """
        self._porcentaje_horas = porcentaje_horas
        self._porcentaje_notas = porcentaje_notas
        self._porcentaje_aprobacion = porcentaje_aprobacion
        self._porcentaje_evaluacion_estudiantil = porcentaje_evaluacion_estudiantil

    def calcular_ponderacion(self, horas: float, notas: bool,
                              aprobacion: float, evaluacion_estudiantil: float) -> float:
        """
        Calcula el puntaje ponderado del desempeño docente.

        Args:
            horas: Porcentaje de horas cumplidas (0.0 - 100.0)
            notas: True si entregó calificaciones oportunamente
            aprobacion: Porcentaje de aprobación del paralelo (0.0 - 100.0)
            evaluacion_estudiantil: Resultado de evaluación estudiantil (0.0 - 100.0)

        Returns:
            Puntaje final ponderado (redondeado a 2 decimales)
        """
        calculo_horas = horas * self._porcentaje_horas
        calculo_aprobacion = aprobacion * self._porcentaje_aprobacion
        calculo_estudiantes = evaluacion_estudiantil * self._porcentaje_evaluacion_estudiantil

        # La entrega oportuna es binaria: suma el porcentaje completo o nada
        calculo_notas = self._porcentaje_notas if notas else 0.0

        return round(
            calculo_horas + calculo_notas + calculo_aprobacion + calculo_estudiantes, 2
        )
