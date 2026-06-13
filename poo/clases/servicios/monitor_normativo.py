from datetime import date

#Enum
from poo.clases.enums.estado_de_alerta import EstadoDeAlerta

from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion


class MonitorNormativo:
    def evaluar_proximidad_vencimiento(self, periodo_de_nivelacion: PeriodoDeNivelacion, fecha_limite: date):
        dias_restantes = (fecha_limite - date.today()).days
        estado = self._obtener_estado_de_alerta(dias_restantes)
        
        return {
            "Periodo de nivelación": periodo_de_nivelacion.periodo,
            "Días restantes": dias_restantes,
            "Estado de alerta": estado.value
        }


    def _obtener_estado_de_alerta(self, dias_restantes: int):
        if dias_restantes < 0:
            return EstadoDeAlerta.CRITICO
        
        if dias_restantes <= 5:
            return EstadoDeAlerta.PREVENTIVO

        return EstadoDeAlerta.NORMAL