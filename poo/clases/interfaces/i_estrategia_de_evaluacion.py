"""
Patrón de comportamiento: Strategy (para evaluación de desempeño)

Define la interfaz que deben implementar las estrategias de cálculo
de puntaje para la evaluación de desempeño docente.

Cada estrategia concreta define sus propios pesos y reglas de
ponderación, permitiendo cambiar el cálculo sin modificar la clase
EvaluacionDeDesempeno.

Implementaciones concretas:
    - EstrategiaDeEvaluacionEstandar: Ponderación configurable por criterio

Principios:
    - ISP: Interfaz mínima (solo calcular_ponderacion)
    - OCP: Nuevas estrategias se crean como nuevas clases
    - LSP: Cualquier estrategia es intercambiable transparentemente
"""

from abc import ABCMeta, abstractmethod


class IEstrategiaDeEvaluacion(metaclass=ABCMeta):
    """
    Interfaz abstracta para estrategias de evaluación de desempeño docente.

    Define el contrato para calcular el puntaje ponderado del desempeño
    de un docente basado en múltiples criterios.
    """

    @abstractmethod
    def calcular_ponderacion(self, horas: float, notas: bool,
                              aprobacion: float, evaluacion_estudiantil: float) -> float:
        """
        Calcula el puntaje ponderado de desempeño docente.

        Args:
            horas: Porcentaje de horas cumplidas (0.0 - 100.0)
            notas: True si entregó calificaciones oportunamente
            aprobacion: Porcentaje de aprobación del paralelo (0.0 - 100.0)
            evaluacion_estudiantil: Resultado de evaluación estudiantil (0.0 - 100.0)

        Returns:
            Puntaje final calculado según la estrategia
        """
        pass
