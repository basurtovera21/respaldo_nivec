#Enum
from clases.enums.estado_de_aprobacion import EstadoDeAprobacion

#Usuario
from clases.usuarios.estudiante import Estudiante

from clases.unidad_curricular import UnidadCurricular


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
        from clases.enums.estado_de_aprobacion import EstadoDeAprobacion

        if self._estado_de_aprobacion != EstadoDeAprobacion.PENDIENTE:
            print(f"[Evaluación académica] No se ha podido registrar (estado {self._estado_de_aprobacion.value}).")
            return

        #Para parcial específico
        if len(args) == 2 and isinstance(args[0], int):
            #(parcial: int, nota: float)
            parcial, nota = args
            self._definir_en_parcial(parcial, nota)
            
        #Para ambos parciales
        elif len(args) == 2 and isinstance(args[0], float):
            #(nota_parcial1: float, nota_parcial2: float)
            self._definir_en_parcial(1, args[0])
            self._definir_en_parcial(2, args[1])

        else:
            print("[Evaluación académica] Registros no válidos para registro.")
            
    def _definir_en_parcial(self, parcial: int, nota: float):
        #Validar rango y definir la nota en el parcial definido
        if not (0.0 <= nota <= 10.0):
            print(f"[Evaluación académica] Nota no válida, fuera de rango (0.0 - 10.0): {nota}")
            return
        
        if parcial == 1:
            self._calificacion_parcial_1 = nota
            print(f"[Evaluación académica] Nota parcial 1 registrada: {nota}")
            
        elif parcial == 2:
            self._calificacion_parcial_2 = nota
            print(f"[Evaluación académica] Nota parcial 2 registrada: {nota}")
        else:
            print(f"[Evaluación académica] Número de parcial no válido: {parcial}")
            
    def calcular_nota_final(self):
        #Promedio de los dos parciales. Actualiza _nota_final.
        if self._calificacion_parcial_1 == 0.0 or self._calificacion_parcial_2 == 0.0:
            print("[Evaluación Académica] No se ha registrado la calificación de ambos parciales.")
            return 0.0
        
        self._nota_final = round((self._calificacion_parcial_1 + self._calificacion_parcial_2)/2, 2)
        return self._nota_final

    def registrar_asistencia_final(self, porcentaje: float):
        #Registro del porcentaje de asistencia. Valor entre 0.0 y 100.0.
        if not (0.0 <= porcentaje <= 100.0):
            print(f"[Evaluación académica] Porcentaje registrado fuera de rango: {porcentaje}")
            return
        
        self._porcentaje_asistencia = porcentaje
        print(f"[EvaluacionAcademica] El porcentaje de asistencia ha sido registrado: {porcentaje}%")

    def verificar_aprobacion(self):
        #Determinación del estado final por criterios normativos en orden de prioridad. Actualiza _estado_de_aprobacion y retorna el estado resultante
        if self._estado_de_aprobacion in (EstadoDeAprobacion.RETIRADO, EstadoDeAprobacion.ANULADO):
            print(f"[Evaluación académica] Estado cerrado: {self._estado_de_aprobacion.value}")
            return self._estado_de_aprobacion

        if self._porcentaje_asistencia < self.unidad_curricular.porcentaje_minimo_asistencia:
            self._estado_de_aprobacion = EstadoDeAprobacion.REPROBADO
            self._observacion = "Reprobado por porcentaje de asistencia insuficiente."
            print(f"[Evaluación académica] {self._observacion}")
            return self._estado_de_aprobacion

        if self._nota_final >= self.unidad_curricular.criterio_de_aprobacion:
            self._estado_de_aprobacion = EstadoDeAprobacion.APROBADO
            
        else:
            self._estado_de_aprobacion = EstadoDeAprobacion.REPROBADO
            self._observacion = "Reprobado por calificación insuficiente."

        print(f"[Evaluacion académica] Estado final: {self._estado_de_aprobacion.value}")
        return self._estado_de_aprobacion