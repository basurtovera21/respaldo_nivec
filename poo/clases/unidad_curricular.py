#Enum
from poo.clases.enums.tipo_de_componente import TipoDeComponente

#Interfaz
from poo.clases.interfaces.i_unidad_evaluable import IUnidadEvaluable


class UnidadCurricular(IUnidadEvaluable):
    def __init__(self, codigo_de_unidad: str, nombre: str, area_de_conocimiento: list, horas_totales: float, horas_semanales: float, horas_sincronicas: float, horas_asincronicas: float, tipo_de_componente: TipoDeComponente, criterio_de_aprobacion: float = 7.0, porcentaje_minimo_asistencia: float = 70.0):
        self.codigo_de_unidad = codigo_de_unidad
        self.nombre = nombre
        self.area_de_conocimiento = area_de_conocimiento
        self.horas_totales = horas_totales
        self.horas_semanales = horas_semanales
        self.horas_sincronicas = horas_sincronicas
        self.horas_asincronicas = horas_asincronicas
        self.tipo_de_componente = tipo_de_componente
        self.criterio_de_aprobacion = criterio_de_aprobacion
        self.porcentaje_minimo_asistencia = porcentaje_minimo_asistencia


    def obtener_codigo_de_unidad(self):
        return self.codigo_de_unidad


    def obtener_horas_totales(self):
        return self.horas_totales


    def validar_distribucion_de_horas_totales(self):
        return (self.horas_sincronicas + self.horas_asincronicas) == self.horas_totales


    def validar_horas(self):
        errores = {}

        if self.horas_totales <= 0:
            errores["horas_totales"] = "Las horas totales deben ser mayor a cero"

        if self.horas_semanales <= 0:
            errores["horas_semanales"] = "Las horas semanales deben ser mayor a cero"

        if self.horas_sincronicas < 0:
            errores["horas_sincronicas"] = "Las horas sincrónicas no pueden ser negativas"

        if self.horas_asincronicas < 0:
            errores["horas_asincronicas"] = "Las horas asincrónicas no pueden ser negativas"

        if not self.validar_distribucion_de_horas_totales():
            errores["horas_totales"] = (
                f"La suma de horas sincrónicas ({self.horas_sincronicas}) y "
                f"asincrónicas ({self.horas_asincronicas}) no coincide con "
                f"el total registrado ({self.horas_totales})"
            )

        return errores


    def validar_criterios(self):
        errores = {}

        if not (0.0 <= self.criterio_de_aprobacion <= 10.0):
            errores["criterio_de_aprobacion"] = "El criterio de aprobación debe estar entre 0.0 y 10.0"

        if not (0.0 <= self.porcentaje_minimo_asistencia <= 100.0):
            errores["porcentaje_minimo_asistencia"] = "El porcentaje mínimo de asistencia debe estar entre 0.0 y 100.0"

        return errores


    def validar_datos_de_registro(self):
        errores = {}

        if not self.nombre or not self.nombre.strip():
            errores["nombre"] = "Información requerida"

        if not self.area_de_conocimiento:
            errores["area_de_conocimiento"] = "Información requerida"

        if not isinstance(self.tipo_de_componente, TipoDeComponente):
            errores["tipo_de_componente"] = "Tipo de componente no válido"

        errores.update(self.validar_horas())
        errores.update(self.validar_criterios())

        return errores


    def recuperar_informacion_de_unidad(self):
        return {
            "Código de unidad": self.codigo_de_unidad,
            "Unidad curricular": self.nombre,
            "Área(s) de conocimiento": self.area_de_conocimiento,
            "Horas totales": self.horas_totales,
            "Horas semanales": self.horas_semanales,
            "Horas sincrónicas": self.horas_sincronicas,
            "Horas asincrónicas": self.horas_asincronicas,
            "Tipo de componente": self.tipo_de_componente.value,
            "Criterio de aprobación": self.criterio_de_aprobacion,
            "Porcentaje mínimo de asistencia": self.porcentaje_minimo_asistencia
        }