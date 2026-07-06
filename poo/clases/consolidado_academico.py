from datetime import date

from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion


class ConsolidadoAcademico:
    """
    Procesa y almacena las estadísticas de un consolidado académico
    a partir de la carga de la Matriz de Tercer Nivel (MTN).

    Uso desde Django (services.py → servicio_procesar_mtn):
        consolidado_poo = ConsolidadoAcademico(periodo, fecha, total_cupos)
        consolidado_poo.cargar_matriz_de_cupos(registros, validos, observados)
        estadisticas = consolidado_poo.obtener_estadisticas_de_consolidado()
    """

    def __init__(self, periodo_academico: PeriodoDeNivelacion, fecha_de_corte: date, total_de_cupos_aceptados: int):
        self.periodo_academico = periodo_academico
        self.fecha_de_corte = fecha_de_corte
        self.total_de_cupos_aceptados = total_de_cupos_aceptados
        self._registros_totales = 0
        self._registros_validos = 0
        self._registros_observados = 0

    def cargar_matriz_de_cupos(self, registros_procesados: list, registros_validos: int, registros_observados: int):
        """Carga los resultados del procesamiento de la MTN."""
        self._registros_totales = len(registros_procesados)
        self._registros_validos = registros_validos
        self._registros_observados = registros_observados

    def obtener_estadisticas_de_consolidado(self) -> dict:
        """Retorna las estadísticas del consolidado para persistir en la BD."""
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
            "Porcentaje de registros válidos": registros_validos,
        }
