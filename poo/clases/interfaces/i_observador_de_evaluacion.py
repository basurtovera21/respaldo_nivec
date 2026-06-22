#Patrón de comportamiento: Observer
#Notificar a varios objetos sobre cualquier evento que le suceda al objeto que está observando
from abc import ABCMeta
from abc import abstractmethod

class IObservadorDeEvaluacion(metaclass = ABCMeta):
    @abstractmethod
    def actualizar(self, evaluacion):
        pass