#Evaluación de desempeño
from poo.clases.interfaces.i_estrategia_de_evaluacion import IEstrategiaDeEvaluacion


class EstrategiaDeEvaluacionEstandar(IEstrategiaDeEvaluacion):
    def __init__(self, porcentaje_horas: float, porcentaje_notas: float, porcentaje_aprobacion: float, porcentaje_evaluacion_estudiantil: float):
        self.porcentaje_horas = porcentaje_horas
        self.porcentaje_notas = porcentaje_notas
        self.porcentaje_aprobacion = porcentaje_aprobacion
        self.porcentaje_evaluacion_estudiantil = porcentaje_evaluacion_estudiantil
      
        
    def calcular_ponderacion(self, horas: float, notas: bool, aprobacion: float, evaluacion_estudiantil: float):
        calculo_horas = horas * self.porcentaje_horas
        calculo_aprobacion = aprobacion * self.porcentaje_aprobacion
        calculo_estudiantes = evaluacion_estudiantil * self.porcentaje_evaluacion_estudiantil
        if notas == True:
            #Porcentaje completo
            calculo_notas = self.porcentaje_notas
        else:
            #No suma
            calculo_notas = 0.0
        
        return round(calculo_horas + calculo_notas + calculo_aprobacion + calculo_estudiantes, 2)