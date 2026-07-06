from datetime import date

from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion


class ConsolidadoAcademico:
    def __init__(self, periodo_academico: PeriodoDeNivelacion, fecha_de_corte: date, total_de_cupos_aceptados: int):
        self.periodo_academico = periodo_academico #Instancia
        self.fecha_de_corte = fecha_de_corte #datetime.date
        self.total_de_cupos_aceptados = total_de_cupos_aceptados
        self._registros_totales = 0
        self._registros_validos = 0
        self._registros_observados = 0
        self._registros_de_entrada = [] #Lista de diccionarios o filas del archivo
        self._indice_de_identificaciones = {}
        

    def cargar_matriz_de_cupos(self, registros_procesados, registro_validos: int, registros_observados: int):
        self._registros_de_entrada = registros_procesados
        self._registros_totales = len(registros_procesados)
        self._registros_validos = registro_validos
        self._registros_observados = registros_observados
        self._indice_de_identificaciones = {}
        for registro in registros_procesados:
            cedula = registro.get("identificacion")
            if cedula:
                self._indice_de_identificaciones[cedula] = registro

    def obtener_estadisticas_de_consolidado(self):
        if self.total_de_cupos_aceptados > 0:
            porcentaje_valido = (self._registros_validos / self.total_de_cupos_aceptados) * 100
            registros_validos = f"{porcentaje_valido:.2f}%"
            
        else:
            registros_validos = "0%"

        return {
            "Fecha de corte": str(self.fecha_de_corte),
            "Cupos aceptados esperados": self.total_de_cupos_aceptados,
            "Registros totales procesados": self._registros_totales,
            "Registros válidos": self._registros_validos,
            "Registros observados": self._registros_observados,
            "Porcentaje de registros válidos": registros_validos
        }