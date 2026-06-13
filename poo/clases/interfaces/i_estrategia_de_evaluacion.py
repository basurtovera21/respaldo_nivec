#EvaluacionDeDesempeno
from abc import ABCMeta
from abc import abstractmethod


class IEstrategiaDeEvaluacion(metaclass = ABCMeta):
    @abstractmethod
    def calcular_ponderacion(self, horas: float, notas: bool, aprobacion: float, evaluacion_estudiantil: float):
        pass