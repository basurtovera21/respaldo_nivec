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
        self.modalidad = modalidad
        self._estado = EstadoDeMalla.DISENO
        self._total_horas_nivelacion = 0.0
        self._unidades_curriculares = []


    def validar_duracion(self):
        return isinstance(self.duracion_semanas, int) and self.duracion_semanas > 0


    def validar_datos_de_registro(self):
        errores = {}

        if not self.nombre or not self.nombre.strip():
            errores["nombre"] = "Información requerida"

        if not self.area_de_conocimiento or not self.area_de_conocimiento.strip():
            errores["area_de_conocimiento"] = "Información requerida"

        if not self.version_de_malla or not self.version_de_malla.strip():
            errores["version_de_malla"] = "Información requerida"

        if not self.validar_duracion():
            errores["duracion_semanas"] = "La duración debe ser un número entero mayor a cero"

        if not isinstance(self.modalidad, Modalidad):
            errores["modalidad"] = "Modalidad no válida"

        return errores


    def clonar(self, nuevo_codigo_de_malla: str, nueva_version_de_malla: str):
        malla_curricular_clonada = copy.deepcopy(self)
        malla_curricular_clonada.codigo_de_malla = nuevo_codigo_de_malla
        malla_curricular_clonada.version_de_malla = nueva_version_de_malla
        malla_curricular_clonada._estado = EstadoDeMalla.DISENO
        return malla_curricular_clonada


    def agregar_unidad_curricular(self, *args):
        unidad_agregada = True
        for entrada in args:
            if isinstance(entrada, list):
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