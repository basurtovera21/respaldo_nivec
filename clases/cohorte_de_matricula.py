from datetime import date

#Enums
from clases.enums.estado_de_cohorte import EstadoDeCohorte
from clases.enums.tipo_de_cohorte import TipoDeCohorte

from clases.periodo_de_nivelacion import PeriodoDeNivelacion
from clases.usuarios.estudiante import Estudiante


class CohorteDeMatricula:
    def __init__(self, codigo_de_registro: str, fecha_de_cierre: date, periodo_de_nivelacion: PeriodoDeNivelacion, tipo_de_cohorte: TipoDeCohorte):
        self.codigo_de_registro = codigo_de_registro
        self.fecha_de_cierre = fecha_de_cierre #Instancia datetime.date
        self.periodo_de_nivelacion = periodo_de_nivelacion #Instancia
        self.tipo_de_cohorte = tipo_de_cohorte   #Instancia TipoDeCohorte
        self._estado_de_cohorte = EstadoDeCohorte.ABIERTA
        self._estudiantes_matriculados = [] #Lista de instancias Estudiante
        self._total_primera_matricula = 0
        self._total_segunda_matricula = 0
        self._total_exonerados = 0
        

    def registrar_estudiante_matriculado(self, estudiante: Estudiante):
        pass
    
    def calcular_total_matriculados(self): #Retorna int
        return (self._total_primera_matricula + self._total_segunda_matricula + self._total_exonerados)