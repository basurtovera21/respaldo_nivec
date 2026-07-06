"""
Servicio de monitoreo normativo para periodos académicos.

Evalúa la proximidad de fechas límite y genera alertas según
el nivel de urgencia:
    - NORMAL: Más de 5 días para el vencimiento
    - PREVENTIVO: 5 días o menos para el vencimiento
    - CRÍTICO: Ya venció (días negativos)

Uso desde Django:
    from poo.clases.servicios.monitor_normativo import MonitorNormativo

    monitor = MonitorNormativo()
    alerta = monitor.evaluar_proximidad_vencimiento(periodo, fecha_limite)
    # alerta["Estado de alerta"] → "Normal" / "Preventivo" / "Crítico"

Principios:
    - SRP: Solo evalúa proximidad de vencimiento y genera alertas
    - OCP: Nuevos umbrales o tipos de alerta se agregan sin modificar la lógica existente
"""

from datetime import date

from poo.clases.enums.estado_de_alerta import EstadoDeAlerta
from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion


class MonitorNormativo:
    """
    Servicio que evalúa la proximidad de vencimiento de fechas académicas
    y genera alertas con distintos niveles de urgencia.
    """

    # ── Constantes de umbrales ──
    UMBRAL_PREVENTIVO_DIAS = 5

    def evaluar_proximidad_vencimiento(self, periodo_de_nivelacion: PeriodoDeNivelacion,
                                        fecha_limite: date) -> dict:
        """
        Evalúa qué tan cerca está una fecha límite y determina el nivel de alerta.

        Args:
            periodo_de_nivelacion: Periodo a evaluar (para contexto del reporte)
            fecha_limite: Fecha contra la cual se evalúa la proximidad

        Returns:
            Diccionario con periodo, días restantes y estado de alerta
        """
        dias_restantes = (fecha_limite - date.today()).days
        estado = self._obtener_estado_de_alerta(dias_restantes)

        return {
            "Periodo de nivelación": periodo_de_nivelacion.periodo,
            "Días restantes": dias_restantes,
            "Estado de alerta": estado.value,
        }

    def _obtener_estado_de_alerta(self, dias_restantes: int) -> EstadoDeAlerta:
        """
        Determina el estado de alerta según los días restantes.

        Reglas:
            - < 0 días → CRITICO (ya venció)
            - ≤ 5 días → PREVENTIVO (próximo a vencer)
            - > 5 días → NORMAL (sin urgencia)
        """
        if dias_restantes < 0:
            return EstadoDeAlerta.CRITICO

        if dias_restantes <= self.UMBRAL_PREVENTIVO_DIAS:
            return EstadoDeAlerta.PREVENTIVO

        return EstadoDeAlerta.NORMAL
