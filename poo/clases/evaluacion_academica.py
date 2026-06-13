#Enum
from poo.clases.enums.estado_de_aprobacion import EstadoDeAprobacion

#Usuario
from poo.clases.usuarios.estudiante import Estudiante

from poo.clases.unidad_curricular import UnidadCurricular


class EvaluacionAcademica:
    def __init__(self, estudiante: Estudiante, unidad_curricular: UnidadCurricular):
        self.estudiante = estudiante #Instancia
        self.unidad_curricular = unidad_curricular #Instancia
        self._calificacion_parcial_1 = 0.0
        self._calificacion_parcial_2 = 0.0
        self._nota_final = 0.0
        self._porcentaje_asistencia = 0.0
        self._estado_de_aprobacion = EstadoDeAprobacion.PENDIENTE
        self._observacion = ""
        

    def registrar_calificacion(self, *args): #Sobrecarga
        if self._estado_de_aprobacion != EstadoDeAprobacion.PENDIENTE:
            return False

        #Para parcial específico
        if len(args) == 2 and isinstance(args[0], int):
            #(parcial: int, nota: float)
            parcial, nota = args
            return self._definir_en_parcial(parcial, nota)
            
        #Para ambos parciales
        elif len(args) == 2 and isinstance(args[0], float):
            #(nota_parcial1: float, nota_parcial2: float)
            resultado_p1 = self._definir_en_parcial(1, args[0])
            resultado_p2 = self._definir_en_parcial(2, args[1])
            return resultado_p1 and resultado_p2

        return False
            
            
    def _definir_en_parcial(self, parcial: int, nota: float):
        #Validar rango y definir la nota en el parcial definido
        if not (0.0 <= nota <= 10.0):
            return False
        
        if parcial == 1:
            self._calificacion_parcial_1 = nota
            return True
            
        elif parcial == 2:
            self._calificacion_parcial_2 = nota
            return True
            
        return False
      
            
    def calcular_nota_final(self):
        #Promedio de los dos parciales. Actualiza _nota_final.
        if self._calificacion_parcial_1 == 0.0 or self._calificacion_parcial_2 == 0.0:
            return 0.0
        
        self._nota_final = round((self._calificacion_parcial_1 + self._calificacion_parcial_2)/2, 2)
        return self._nota_final


    def registrar_asistencia_final(self, porcentaje: float):
        #Registro del porcentaje de asistencia. Valor entre 0.0 y 100.0.
        if not (0.0 <= porcentaje <= 100.0):
            return False
        
        self._porcentaje_asistencia = porcentaje
        return True


    def verificar_aprobacion(self):
        #Determinación del estado final por criterios normativos en orden de prioridad. Actualiza _estado_de_aprobacion y retorna el estado resultante
        if self._estado_de_aprobacion in (EstadoDeAprobacion.RETIRADO, EstadoDeAprobacion.ANULADO):
            return self._estado_de_aprobacion

        if self._porcentaje_asistencia < self.unidad_curricular.porcentaje_minimo_asistencia:
            self._estado_de_aprobacion = EstadoDeAprobacion.REPROBADO
            self._observacion = "Reprobado por porcentaje de asistencia insuficiente."
            return self._estado_de_aprobacion

        if self._nota_final >= self.unidad_curricular.criterio_de_aprobacion:
            self._estado_de_aprobacion = EstadoDeAprobacion.APROBADO
            
        else:
            self._estado_de_aprobacion = EstadoDeAprobacion.REPROBADO
            self._observacion = "Reprobado por calificación insuficiente."

        return self._estado_de_aprobacion
    
    
    def obtener_resumen_de_evaluacion(self):
        return {
            "Estudiante": f"{self.estudiante.nombres} {self.estudiante.apellidos}",
            "Unidad_curricular": self.unidad_curricular.nombre,
            "Calificación parcial 1": self._calificacion_parcial_1,
            "Calificación parcial 2": self._calificacion_parcial_2,
            "Nota final": self._nota_final,
            "Porcentaje de asistencia": self._porcentaje_asistencia,
            "Estado de aprobación": self._estado_de_aprobacion.value,
            "Observación": self._observacion,
        }
        
    
    @classmethod
    def registrar_evaluacion_de_paralelo(cls, evaluaciones_academicas: list):
        evaluacion_de_paralelo = []
        
        for evaluacion_academica in evaluaciones_academicas:
            resumen_de_estudiante = evaluacion_academica.obtener_resumen_de_evaluacion()
            evaluacion_de_paralelo.append(resumen_de_estudiante)
            
        return evaluacion_de_paralelo