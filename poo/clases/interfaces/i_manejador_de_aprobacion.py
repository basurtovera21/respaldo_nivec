#Patrón de comportamiento: Chain of Responsibility
#Al recibir una solicitud, cada manejador decide si la procesa o si la pasa al siguiente manejador de la cadena
from abc import ABCMeta
from abc import abstractmethod

class IManejadorDeAprobacion(metaclass = ABCMeta):
    def __init__(self, siguiente = None):
        self.siguiente = siguiente #referencia al siguiente manejador

    @abstractmethod
    def manejar(self, evaluacion):
        pass