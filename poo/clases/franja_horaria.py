from datetime import time

from poo.clases.enums.jornada import Jornada
from poo.clases.enums.dia_de_semana import DiaDeSemana


# Duración mínima y máxima de una sesión (bloque) en un mismo día.
MIN_HORAS_POR_SESION = 1.0
MAX_HORAS_POR_SESION = 3.0

# Duraciones permitidas para una sesión (horas enteras). El generador solo usa estas.
DURACIONES_VALIDAS = [1, 2, 3]

# Franja horaria permitida por jornada (patrón semanal). No cruzan medianoche
# para que la aritmética de solape sea trivial.
FRANJAS = {
    Jornada.MATUTINA: (time(7, 0), time(13, 0)),
    Jornada.VESPERTINA: (time(13, 0), time(19, 0)),
    Jornada.NOCTURNA: (time(19, 0), time(23, 0)),
}

# Días hábiles para la generación automática de horarios (lunes a viernes).
# Sábados y domingos no se consideran.
DIAS_HABILES = [
    DiaDeSemana.LUNES,
    DiaDeSemana.MARTES,
    DiaDeSemana.MIERCOLES,
    DiaDeSemana.JUEVES,
    DiaDeSemana.VIERNES,
]


def obtener_franja(jornada: Jornada):
    return FRANJAS.get(jornada)


def obtener_dias_habiles():
    """Retorna los días hábiles disponibles para generación de horarios (lunes a viernes)."""
    return list(DIAS_HABILES)


def sesion_dentro_de_franja(jornada: Jornada, hora_inicio: time, hora_fin: time) -> bool:
    franja = FRANJAS.get(jornada)
    if not franja:
        return True
    inicio, fin = franja
    return hora_inicio >= inicio and hora_fin <= fin


def texto_franja(jornada: Jornada) -> str:
    franja = FRANJAS.get(jornada)
    if not franja:
        return ""
    inicio, fin = franja
    return f"{inicio.strftime('%H:%M')} - {fin.strftime('%H:%M')}"


def calcular_horas_maximas_semanales(jornada: Jornada) -> float:
    """
    Calcula el máximo de horas semanales disponibles para una jornada,
    considerando solo días hábiles (lunes a viernes) y sesiones de hasta 3 horas por día.
    """
    franja = FRANJAS.get(jornada)
    if not franja:
        return 0.0
    inicio, fin = franja
    horas_por_dia = fin.hour - inicio.hour
    # Una unidad no puede tener más de MAX_HORAS_POR_SESION por día
    horas_efectivas_por_dia = min(horas_por_dia, MAX_HORAS_POR_SESION)
    dias = len(DIAS_HABILES)
    return horas_efectivas_por_dia * dias


def validar_horas_semanales_unidad(horas_semanales: float, jornada: Jornada) -> dict:
    """
    Valida si las horas sincrónicas semanales de una unidad caben dentro de la
    franja de la jornada considerando solo días hábiles y el máximo por sesión.
    
    Retorna: {"ok": True} o {"ok": False, "motivo": str, "maximo": float}
    """
    maximo = calcular_horas_maximas_semanales(jornada)
    if horas_semanales <= maximo:
        return {"ok": True}
    return {
        "ok": False,
        "motivo": f"Las horas sincrónicas semanales ({horas_semanales}h) exceden el máximo disponible ({maximo}h) para la jornada {jornada.value} (5 días × {int(MAX_HORAS_POR_SESION)}h por sesión)",
        "maximo": maximo,
    }
