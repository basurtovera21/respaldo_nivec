from abc import ABCMeta
from poo.clases.interfaces.i_observador_de_evaluacion import IObservadorDeEvaluacion

class ISujetoDeEvaluacion(metaclass = ABCMeta):
    def __init__(self):
        self._observadores = [] #Lista de observadores

    def anexar(self, observador: IObservadorDeEvaluacion):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def remover(self, observador: IObservadorDeEvaluacion):
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self):
        for obs in self._observadores:
            obs.actualizar(self)  #Se pasa a sí mismo (la instancia del sujeto)