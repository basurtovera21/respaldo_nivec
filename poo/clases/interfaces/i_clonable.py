#Malla curricular
from abc import ABCMeta
from abc import abstractmethod


class IClonable(metaclass = ABCMeta):

    @abstractmethod
    def clonar(self):
        pass