from abc import ABCMeta
from abc import abstractmethod


class IUnidadEvaluable(metaclass = ABCMeta):
    @abstractmethod
    def obtener_codigo_de_unidad(self):
        pass


    @abstractmethod
    def obtener_horas_totales(self):
        pass