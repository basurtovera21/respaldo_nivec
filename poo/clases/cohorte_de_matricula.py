from datetime import date

#Enums
from poo.clases.enums.estado_de_cohorte import EstadoDeCohorte
from poo.clases.enums.tipo_de_cohorte import TipoDeCohorte
from poo.clases.enums.registro_de_cupo import RegistroDeCupo

from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion
from poo.clases.usuarios.estudiante import Estudiante
from poo.clases.carrera import Carrera


class CohorteDeMatricula:
    def __init__(self, codigo_de_registro: str, nombre_cohorte: str, carrera_registrada: Carrera, fecha_de_cierre: date, periodo_de_nivelacion: PeriodoDeNivelacion, tipo_de_cohorte: TipoDeCohorte):
        self.codigo_de_registro = codigo_de_registro
        self.nombre_cohorte = nombre_cohorte
        self.carrera_registrada = carrera_registrada
        self.fecha_de_cierre = fecha_de_cierre #datetime.date
        self.periodo_de_nivelacion = periodo_de_nivelacion #Instancia
        self.tipo_de_cohorte = tipo_de_cohorte   #Instancia
        self._estado_de_cohorte = EstadoDeCohorte.ABIERTA
        self._estudiantes_matriculados = [] #Lista de instancias Estudiante
        self._total_primera_matricula = 0
        self._total_segunda_matricula = 0
        self._total_exonerados = 0
        

    def registrar_estudiante_matriculado(self, estudiante: Estudiante):
        if self._estado_de_cohorte != EstadoDeCohorte.ABIERTA:
            return False

        if date.today() > self.fecha_de_cierre:
            return False

        if estudiante in self._estudiantes_matriculados:
            return False

        self._estudiantes_matriculados.append(estudiante)
        self._actualizar_contador_de_registro(estudiante.registro_de_cupo)
        return True
        
        
    def _actualizar_contador_de_registro(self, registro_de_cupo: RegistroDeCupo):
        if registro_de_cupo == RegistroDeCupo.REGULAR:
            self._total_primera_matricula += 1

        elif registro_de_cupo == RegistroDeCupo.SEGUNDA_MATRICULA:
            self._total_segunda_matricula += 1

        elif registro_de_cupo == RegistroDeCupo.EXONERACION:
            self._total_exonerados += 1    
            
            
    def calcular_total_matriculados(self):
        return (self._total_primera_matricula + self._total_segunda_matricula + self._total_exonerados)
    
    
    def obtener_estadisticas_de_registro(self):
        return {
            "Total primera matricula": self._total_primera_matricula,
            "Total segunda matricula": self._total_segunda_matricula,
            "Total exonerados": self._total_exonerados,
            "Estudiantes matriculados": self.calcular_total_matriculados()
        }