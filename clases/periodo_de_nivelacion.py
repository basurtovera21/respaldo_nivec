<<<<<<< Updated upstream
=======
from datetime import date

# Enums
from clases.enums.estado_de_periodo import EstadoDePeriodo
from clases.enums.modalidad import Modalidad


class PeriodoDeNivelacion:
    def __init__(
        self,
        codigo_periodo: str,
        anio: int,
        periodo: str,
        fecha_inicio: date,
        fecha_fin: date,
        modalidad: Modalidad,
        numero_periodo: int,
    ):
        self.codigo_periodo = codigo_periodo
        self.anio = anio
        self.periodo = periodo
        self.fecha_inicio = fecha_inicio  # Instancia de datetime.date
        self.fecha_fin = fecha_fin  # Instancia de datetime.date
        self.modalidad = modalidad  # Instancia
        self.numero_periodo = numero_periodo  # (1 o 2)
        self._estado = EstadoDePeriodo.PLANIFICACION

    def iniciar_periodo(self):
        pass

    def finalizar_periodo(self):
        pass

    def calcular_duracion_semanas(self):  # Retorna int
        diferencia_tiempo = self.fecha_fin - self.fecha_inicio
        total_días = diferencia_tiempo.days
        semanas_totales = total_días // 7
        return semanas_totales

    def calcular_total_cupos_ofertados(
        self,
    ):  # (primera + segunda matrícula + exoneración) Retorna int
        pass
>>>>>>> Stashed changes
