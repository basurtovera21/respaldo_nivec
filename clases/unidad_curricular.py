#Enum
from clases.enums.tipo_de_componente import TipoDeComponente


class UnidadCurricular:
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
        

    def validar_distribucion_de_horas_totales(self): #Retorna bool
        suma_horas = self.horas_sincronicas + self.horas_asincronicas
        
        if suma_horas == self.horas_totales:
            return True
        else:
            return False

    def visualizar_detalles_de_configuracion(self): #Retorna dict
        pass