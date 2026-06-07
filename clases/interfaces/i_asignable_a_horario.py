#Horario
from abc import ABCMeta
from abc import abstractmethod

class IAsignableAHorario(metaclass = ABCMeta):
    @property
    @abstractmethod
    def nombres(self):
        pass

    @property
    @abstractmethod
    def apellidos(self):
        pass