"""
Patrón de comportamiento: Observer (Sujeto)

El sujeto mantiene una lista de observadores y los notifica automáticamente
cuando ocurre un cambio de estado relevante. En este sistema, EvaluacionAcademica
es el sujeto que notifica cuando el estado de aprobación cambia de PENDIENTE.

Componentes del patrón:
    - ISujetoDeEvaluacion (esta clase): Mantiene y notifica observadores
    - IObservadorDeEvaluacion: Interfaz que implementan los observadores concretos
    - ObservadorEstadoEstudiante, ObservadorInformeGeneral: Observadores concretos
"""

from abc import ABCMeta
from poo.clases.interfaces.i_observador_de_evaluacion import IObservadorDeEvaluacion


class ISujetoDeEvaluacion(metaclass=ABCMeta):
    """
    Clase abstracta que implementa la mecánica del patrón Observer (lado Sujeto).

    Cualquier clase que herede de ISujetoDeEvaluacion puede:
        - Registrar observadores (anexar)
        - Remover observadores (remover)
        - Notificar a todos los observadores cuando ocurra un evento relevante
    """

    def __init__(self):
        self._observadores = []

    def anexar(self, observador: IObservadorDeEvaluacion):
        """Registra un observador para recibir notificaciones."""
        if observador not in self._observadores:
            self._observadores.append(observador)

    def remover(self, observador: IObservadorDeEvaluacion):
        """Remueve un observador de la lista de notificaciones."""
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self):
        """Notifica a todos los observadores suscritos, pasándose a sí mismo como contexto."""
        for observador in self._observadores:
            observador.actualizar(self)
