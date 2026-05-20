#Tony
#Enums
from clases.enums.jornada import Jornada
from clases.enums.modalidad import Modalidad

#Usuarios
from clases.usuarios.docente import Docente
from clases.usuarios.estudiante import Estudiante


class Paralelo:
    def __init__(self, codigo_de_paralelo: str, nombre: str, jornada: Jornada, modalidad: Modalidad, capacidad_maxima: int):
        self.codigo_de_paralelo = codigo_de_paralelo
        self.nombre = nombre
        self.jornada = jornada #Instancia
        self.modalidad = modalidad #Instancia
        self.capacidad_maxima = capacidad_maxima
        self._docente_responsable = None #Instancia Docente
        self._estudiantes_matriculados = [] #Lista de instancias Estudiante
        

    def tiene_cupo_disponible(self): #Retorna bool
        total_matriculados = len(self._estudiantes_matriculados)
        
        if total_matriculados < self.capacidad_maxima:
            return True
        else:
            return False
            
    def vincular_estudiante(self): #self, estudiante: Estudiante
        pass  
    def desvincular_estudiante(self): #self, estudiante: Estudiante
        pass
    def vincular_docente(self): #self, docente: Docente
        pass
