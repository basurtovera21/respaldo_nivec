#Interfaz
from poo.clases.interfaces.i_unidad_evaluable import IUnidadEvaluable

class UnidadCurricular(IUnidadEvaluable):
    def __init__(self, codigo_de_unidad: str, nombre: str, area_de_conocimiento: list, horas_totales: float, horas_sincronicas: float, horas_asincronicas: float, criterio_de_aprobacion: float = 7.0, porcentaje_minimo_asistencia: float = 70.0):
        self.codigo_de_unidad = codigo_de_unidad
        self.nombre = nombre
        self.area_de_conocimiento = area_de_conocimiento
        self.horas_totales = horas_totales
        self.horas_sincronicas = horas_sincronicas
        self.horas_asincronicas = horas_asincronicas
        self.criterio_de_aprobacion = criterio_de_aprobacion
        self.porcentaje_minimo_asistencia = porcentaje_minimo_asistencia

    def obtener_codigo_de_unidad(self):
        return self.codigo_de_unidad

    def obtener_horas_totales(self):
        return self.horas_totales

    def validar_distribucion_de_horas_totales(self):
        from poo.clases.criterios_filtro.criterio_consistente_de_horas import CriterioConsistenteDeHoras

        criterio = CriterioConsistenteDeHoras()
        return criterio.es_valido({
            "horas_totales": self.horas_totales,
            "horas_sincronicas": self.horas_sincronicas,
            "horas_asincronicas": self.horas_asincronicas,
        })


    def validar_horas(self):
        errores = {}

        if self.horas_totales <= 0:
            errores["horas_totales"] = "el registro debe ser mayor a cero"

        if self.horas_sincronicas < 0:
            errores["horas_sincronicas"] = "el registro no puede ser negativo"

        if self.horas_asincronicas < 0:
            errores["horas_asincronicas"] = "el registro no puede ser negativo"

        if not self.validar_distribucion_de_horas_totales():
            errores["horas_totales"] = (
                f"el total de horas sincrónicas y horas asincrónicas no coincide con el total registrado"
            )

        return errores

    def validar_criterios(self):
        errores = {}

        if not (0.0 <= self.criterio_de_aprobacion <= 10.0):
            errores["criterio_de_aprobacion"] = "el registro debe estar entre 0.0 y 10.0"

        if not (0.0 <= self.porcentaje_minimo_asistencia <= 100.0):
            errores["porcentaje_minimo_asistencia"] = "el registro debe estar entre 0.0 y 100.0"

        return errores

    def validar_datos_de_registro(self):
        errores = {}

        if not self.nombre or not self.nombre.strip():
            errores["nombre"] = "Información requerida"

        if not self.area_de_conocimiento:
            errores["area_de_conocimiento"] = "Información requerida"

        errores.update(self.validar_horas())
        errores.update(self.validar_criterios())

        return errores

    def recuperar_informacion_de_unidad(self):
        return {
            "Código de unidad": self.codigo_de_unidad,
            "Unidad curricular": self.nombre,
            "Área(s) de conocimiento": self.area_de_conocimiento,
            "Horas totales": self.horas_totales,
            "Horas sincrónicas": self.horas_sincronicas,
            "Horas asincrónicas": self.horas_asincronicas,
            "Criterio de aprobación": self.criterio_de_aprobacion,
            "Porcentaje mínimo de asistencia": self.porcentaje_minimo_asistencia
        }