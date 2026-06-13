#Enum
from poo.clases.enums.tipo_de_componente import TipoDeComponente

#Interfaz
from poo.clases.interfaces.i_unidad_evaluable import IUnidadEvaluable


class UnidadCurricular(IUnidadEvaluable):
    def __init__(self, codigo_de_unidad: str, nombre: str, area_de_conocimiento: list, horas_totales: float, horas_semanales: float, horas_sincronicas: float, horas_asincronicas: float, tipo_de_componente: TipoDeComponente, criterio_de_aprobacion: float = 7.0, porcentaje_minimo_asistencia: float = 70.0):
        self.codigo_de_unidad = codigo_de_unidad
        self.nombre = nombre
        self.area_de_conocimiento = area_de_conocimiento #Lista
        self.horas_totales = horas_totales
        self.horas_semanales = horas_semanales
        self.horas_sincronicas = horas_sincronicas
        self.horas_asincronicas = horas_asincronicas
        self.tipo_de_componente = tipo_de_componente #Instancia
        self.criterio_de_aprobacion = criterio_de_aprobacion
        self.porcentaje_minimo_asistencia = porcentaje_minimo_asistencia
        

    def obtener_codigo_de_unidad(self):
        return self.codigo_de_unidad


    def obtener_horas_totales(self):
        return self.horas_totales


    def validar_distribucion_de_horas_totales(self):
        calculo_horas_totales = self.horas_sincronicas + self.horas_asincronicas
        if calculo_horas_totales == self.horas_totales:
            return True
        
        else:
            return False


    def recuperar_informacion_de_unidad(self):
        return {
            "Código de unidad": self.codigo_de_unidad,
            "Unidad curricular": self.nombre,
            "Área(s) de conocimiento": self.area_de_conocimiento, # Lista
            "Horas totales": self.horas_totales,
            "Horas semanales": self.horas_semanales,
            "Horas sincrónicas": self.horas_sincronicas,
            "Horas asincrónicas": self.horas_asincronicas,
            "Tipo de componente": self.tipo_de_componente.value, # Valor del Enum
            "Criterio de aprobación": self.criterio_de_aprobacion,
            "Porcentaje mínimo de asistencia": self.porcentaje_minimo_asistencia
            }