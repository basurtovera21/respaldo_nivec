from abc import ABCMeta
from abc import abstractmethod


class IInformeInstitucional(metaclass = ABCMeta):
    @abstractmethod
    def emitir_informe_de_nivelacion(self):
        pass