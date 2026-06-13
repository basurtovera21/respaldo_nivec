#Enums
from poo.clases.enums.jornada import Jornada
from poo.clases.enums.modalidad import Modalidad

#Usuarios
from poo.clases.usuarios.docente import Docente
from poo.clases.usuarios.estudiante import Estudiante
#import Carrera

from poo.clases.horario import Horario


class Paralelo:
    def __init__(self, codigo_de_paralelo: str, nombre: str, jornada: Jornada, modalidad: Modalidad, capacidad_maxima: int): #carrera: Carrera
        self.codigo_de_paralelo = codigo_de_paralelo
        self.nombre = nombre
        self.jornada = jornada #Instancia
        self.modalidad = modalidad #Instancia
        self.capacidad_maxima = capacidad_maxima
        #self.carrera = carrera
        self._docente_responsable = None #Instancia Docente
        self._estudiantes_matriculados = [] #Lista de instancias Estudiante
        self.horarios = []
        

    def tiene_cupo_disponible(self): #Retorna bool
        total_matriculados = len(self._estudiantes_matriculados)
        if total_matriculados < self.capacidad_maxima:
            return True
        
        else:
            return False
        
            
    def vincular_estudiante(self, estudiante: Estudiante):
        if not self.tiene_cupo_disponible():
            return False

        if estudiante in self._estudiantes_matriculados:
            return False

        self._estudiantes_matriculados.append(estudiante)
        return True
        
        
    def desvincular_estudiante(self, estudiante: Estudiante):
        if estudiante not in self._estudiantes_matriculados:
            return False

        self._estudiantes_matriculados.remove(estudiante)
        return True
        
    
    def vincular_docente(self, docente: Docente):
        if self._docente_responsable is not None:
            return False

        self._docente_responsable = docente
        return True
    
    
    def agregar_horario(self, horario: Horario):
        self.horarios.append(horario)


    def obtener_resumen_horario(self):
        lista_de_resumenes_horarios = []
        
        for horario in self.horarios:
            resumen_de_la_sesion = horario.obtener_resumen_de_sesion()
            lista_de_resumenes_horarios.append(resumen_de_la_sesion)
            
        return lista_de_resumenes_horarios