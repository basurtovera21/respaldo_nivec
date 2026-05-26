#Enums
from clases.enums.estado_de_malla import EstadoDeMalla
from clases.enums.modalidad import Modalidad

from clases.unidad_curricular import UnidadCurricular


class MallaCurricular:
    def __init__(self, codigo_de_malla: str, nombre: str, area_de_conocimiento: str, duracion_semanas: int, version_de_malla: str, modalidad: Modalidad):
        self.codigo_de_malla = codigo_de_malla
        self.nombre = nombre
        self.area_de_conocimiento = area_de_conocimiento
        self.duracion_semanas = duracion_semanas
        self.version_de_malla = version_de_malla
        self.modalidad = modalidad
        self._estado = EstadoDeMalla.DISENO
        self._total_horas_nivelacion = 0.0
        self._unidades_curriculares = [] #Lista unidades curriculares
        

    def agregar_unidad_curricular(self, *args): #Sobrecarga
        for entrada in args:
            if isinstance(entrada, list):
                #Lista como argumento único
                for unidad in entrada:
                    self._agregar_una(unidad)
            else:
                self._agregar_una(entrada)
                
    def _agregar_una(self, unidad_curricular):
        from clases.enums.estado_de_malla import EstadoDeMalla
        from clases.unidad_curricular import UnidadCurricular

        if self._estado not in (EstadoDeMalla.DISENO, EstadoDeMalla.ACTIVA):
            print(f"[Malla curricular] No se puede modificar (estado actual '{self._estado.value})'")
            return
        
        if not isinstance(unidad_curricular, UnidadCurricular):
            print(f"[Malla curricular] Entrada no válida (se esperaba UnidadCurricular).")
            return
        
        codigos_de_mallas_existentes = [unidad.codigo_de_unidad for unidad in self._unidades_curriculares]
        if unidad_curricular.codigo_de_unidad in codigos_de_mallas_existentes:
            print(f"[Malla curricular] La unidad ya ha sido registrada: {unidad_curricular.codigo_de_unidad}")
            return
        
        self._unidades_curriculares.append(unidad_curricular)
        
        self._total_horas_nivelacion = self.calcular_total_horas_nivelacion()
        
        print(f"[Malla curricular] Unidad registrada: {unidad_curricular.nombre}")
            
    def calcular_total_horas_nivelacion(self):
        return sum(unidad.horas_totales for unidad in self._unidades_curriculares)