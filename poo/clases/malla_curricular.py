#Patrón creacional "Prototype"
import copy

# Enums
from poo.clases.enums.estado_de_malla import EstadoDeMalla
from poo.clases.enums.modalidad import Modalidad

# Interfaces
from poo.clases.interfaces.i_unidad_evaluable import IUnidadEvaluable
from poo.clases.interfaces.i_clonable import IClonable

class MallaCurricular(IClonable):
    def __init__(self, codigo_de_malla: str, nombre: str, version_de_malla: str):
        self.codigo_de_malla = codigo_de_malla
        self.nombre = nombre
        self.version_de_malla = version_de_malla
        self._estado = EstadoDeMalla.DISENO
        self._total_horas_nivelacion = 0.0
        self._unidades_curriculares = []


    @property
    def estado(self):
        return self._estado

    @property
    def total_horas_nivelacion(self):
        return self._total_horas_nivelacion

    def establecer_estado(self, estado: EstadoDeMalla):
        if isinstance(estado, EstadoDeMalla):
            self._estado = estado
            return True
        return False

    def puede_editar_estructura(self):
        return self._estado in (EstadoDeMalla.DISENO, EstadoDeMalla.ACTIVA)

    def esta_activa(self):
        return self._estado == EstadoDeMalla.ACTIVA

    def puede_usarse_en_paralelos(self):
        return self._estado == EstadoDeMalla.ACTIVA

    def activar(self):
        if self._estado in (EstadoDeMalla.DISENO, EstadoDeMalla.INACTIVA):
            self._estado = EstadoDeMalla.ACTIVA
            return True
        return False

    def marcar_historica(self):
        if self._estado == EstadoDeMalla.ACTIVA:
            self._estado = EstadoDeMalla.HISTORICA
            return True
        return False

    def inactivar(self):
        if self._estado in (EstadoDeMalla.DISENO, EstadoDeMalla.ACTIVA):
            self._estado = EstadoDeMalla.INACTIVA
            return True
        return False

    def validar_datos_de_registro(self):
        errores = {}

        if not self.nombre or not self.nombre.strip():
            errores["nombre"] = "Información requerida"

        return errores

    #Patrón Prototype
    def clonar(self, nuevo_codigo_de_malla: str, nueva_version_de_malla: str):
        malla_curricular_clonada = copy.deepcopy(self)
        malla_curricular_clonada.codigo_de_malla = nuevo_codigo_de_malla
        malla_curricular_clonada.version_de_malla = nueva_version_de_malla
        malla_curricular_clonada._estado = EstadoDeMalla.DISENO
        malla_curricular_clonada._total_horas_nivelacion = malla_curricular_clonada.calcular_total_horas_nivelacion()
        return malla_curricular_clonada

 
    def obtener_unidades_curriculares(self):
        return list(self._unidades_curriculares)

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
        if not self.puede_editar_estructura():
            return False

        if not isinstance(unidad_curricular, IUnidadEvaluable):
            return False

        for unidad in self._unidades_curriculares:
            if unidad.obtener_codigo_de_unidad() == unidad_curricular.obtener_codigo_de_unidad():
                return False

        self._unidades_curriculares.append(unidad_curricular)
        self._total_horas_nivelacion = self.calcular_total_horas_nivelacion()
        return True

    def calcular_total_horas_nivelacion(self):
        calculo_total_horas_nivelacion = 0.0

        for unidad in self._unidades_curriculares:
            calculo_total_horas_nivelacion += unidad.obtener_horas_totales()

        return calculo_total_horas_nivelacion

    def calcular_total_horas_sincronicas(self):
        """Suma de horas sincrónicas de todas las unidades curriculares."""
        total = 0.0
        for unidad in self._unidades_curriculares:
            total += unidad.horas_sincronicas
        return total

    def validar_compatibilidad_horaria(self, semanas: int):
        """
        Valida si la malla puede generar un horario viable en cualquier jornada,
        dado un número de semanas de periodo.

        Utiliza el límite de 20h sincrónicas semanales definido en franja_horaria.

        Args:
            semanas: Número de semanas del periodo de referencia

        Returns:
            {"ok": True, "horas_semanales": float, "limite": int} si es compatible
            {"ok": False, "motivo": str, "horas_semanales": float, "limite": int} si no es compatible
        """
        from poo.clases.franja_horaria import validar_malla_cabe_en_horario

        total_sincronicas = self.calcular_total_horas_sincronicas()
        return validar_malla_cabe_en_horario(total_sincronicas, semanas)