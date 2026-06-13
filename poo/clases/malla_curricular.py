#Patrón creacional "Prototype"
import copy

# Enums
from poo.clases.enums.estado_de_malla import EstadoDeMalla
from poo.clases.enums.modalidad import Modalidad

# Interfaces
from poo.clases.interfaces.i_unidad_evaluable import IUnidadEvaluable
from poo.clases.interfaces.i_clonable import IClonable


class MallaCurricular(IClonable):
    def __init__(self, codigo_de_malla: str, nombre: str, area_de_conocimiento: str, duracion_semanas: int, version_de_malla: str, modalidad: Modalidad):
        self.codigo_de_malla = codigo_de_malla
        self.nombre = nombre
        self.area_de_conocimiento = area_de_conocimiento
        self.duracion_semanas = duracion_semanas
        self.version_de_malla = version_de_malla
        self.modalidad = modalidad #Instancia
        self._estado = EstadoDeMalla.DISENO
        self._total_horas_nivelacion = 0.0
        self._unidades_curriculares = [] #Lista unidades curriculares


    def clonar(self, nuevo_codigo_de_malla: str, nueva_version_de_malla: str):
        malla_curricular_clonada = copy.deepcopy(self)
        malla_curricular_clonada.codigo_de_malla = nuevo_codigo_de_malla
        malla_curricular_clonada.version_de_malla = nueva_version_de_malla
        malla_curricular_clonada._estado = EstadoDeMalla.DISENO
        return malla_curricular_clonada


    def agregar_unidad_curricular(self, *args): #Sobrecarga
        unidad_agregada = True
        for entrada in args:
            if isinstance(entrada, list):
                #Lista como argumento único
                for unidad in entrada:
                    if not self._agregar_una_unidad_curricular(unidad):
                        unidad_agregada = False
                        
            else:
                if not self._agregar_una_unidad_curricular(entrada):
                    unidad_agregada = False
        
        return unidad_agregada
                
                
    def _agregar_una_unidad_curricular(self, unidad_curricular: IUnidadEvaluable):
        if self._estado not in (EstadoDeMalla.DISENO, EstadoDeMalla.ACTIVA):
            return False

        if not isinstance(unidad_curricular, IUnidadEvaluable):
            return False

        for unidad in self._unidades_curriculares:
            if unidad.codigo_de_unidad == unidad_curricular.codigo_de_unidad:
                return False

        self._unidades_curriculares.append(unidad_curricular)
        self._total_horas_nivelacion = self.calcular_total_horas_nivelacion()
        return True
       
            
    def calcular_total_horas_nivelacion(self):
        calculo_total_horas_nivelacion = 0.0

        for unidad in self._unidades_curriculares:
            calculo_total_horas_nivelacion += unidad.obtener_horas_totales()

        return calculo_total_horas_nivelacion