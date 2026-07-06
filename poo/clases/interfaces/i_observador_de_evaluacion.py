"""
Patrón de comportamiento: Observer (Observador)

Define la interfaz que deben implementar todos los objetos que deseen
ser notificados cuando una evaluación académica cambie de estado.

Implementaciones concretas:
    - ObservadorEstadoEstudiante: Reacciona al cambio de estado del estudiante
    - ObservadorInformeGeneral: Registra datos para procesamiento de informes
"""

from abc import ABCMeta, abstractmethod


class IObservadorDeEvaluacion(metaclass=ABCMeta):
    """
    Interfaz abstracta para observadores del patrón Observer.

    Cada observador concreto debe implementar actualizar() para definir
    su reacción ante el cambio de estado de una evaluación académica.
    """

    @abstractmethod
    def actualizar(self, evaluacion):
        """
        Método invocado automáticamente cuando el sujeto notifica un cambio.

        Args:
            evaluacion: La instancia de EvaluacionAcademica que cambió de estado
        """
        pass
