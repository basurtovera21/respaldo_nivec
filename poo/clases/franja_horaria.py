import math
from datetime import time

from poo.clases.enums.jornada import Jornada
from poo.clases.enums.dia_de_semana import DiaDeSemana


# ══════════════════════════════════════════════════════════════
# CONSTANTES DE CONFIGURACIÓN DE HORARIOS
# ══════════════════════════════════════════════════════════════

# Duración mínima y máxima de una sesión (bloque) en un mismo día.
MIN_HORAS_POR_SESION = 1.0
MAX_HORAS_POR_SESION = 3.0

# Duraciones permitidas para una sesión (horas enteras).
DURACIONES_VALIDAS = [1, 2, 3]

# Franja horaria permitida por jornada (lunes a viernes).
FRANJAS = {
    Jornada.MATUTINA: (time(7, 0), time(13, 0)),
    Jornada.VESPERTINA: (time(13, 0), time(19, 0)),
    Jornada.NOCTURNA: (time(19, 0), time(23, 0)),
}

# Franja adicional del sábado para jornada nocturna (compensación).
FRANJA_SABADO_NOCTURNA = (time(8, 0), time(13, 0))  # 5 horas

# Días hábiles para la generación automática de horarios (lunes a viernes).
DIAS_HABILES = [
    DiaDeSemana.LUNES,
    DiaDeSemana.MARTES,
    DiaDeSemana.MIERCOLES,
    DiaDeSemana.JUEVES,
    DiaDeSemana.VIERNES,
]

# ══════════════════════════════════════════════════════════════
# LÍMITE DE HORAS SINCRÓNICAS SEMANALES POR MALLA
# ══════════════════════════════════════════════════════════════
# Este límite garantiza que TODAS las unidades de una malla puedan
# tener sus sesiones sin solapamiento, en cualquier jornada posible.
#
# Cálculo:
#   - Nocturna (la más restrictiva): 4h/día × 5 días + 5h sábado = 25h disponibles
#   - Margen de seguridad (~80%): 25h × 0.80 ≈ 20h
#   - Resultado: 20h semanales como límite universal
#
# Con 8 semanas de periodo → máximo 160h sincrónicas totales por malla
# Con 12 semanas de periodo → máximo 240h sincrónicas totales por malla

LIMITE_HORAS_SINCRONICAS_SEMANALES_MALLA = 20

# Número mínimo de semanas para el cálculo del límite (referencia estándar)
SEMANAS_REFERENCIA_MINIMA = 8


# ══════════════════════════════════════════════════════════════
# FUNCIONES DE CONSULTA DE FRANJAS
# ══════════════════════════════════════════════════════════════

def obtener_franja(jornada: Jornada):
    """Retorna la tupla (hora_inicio, hora_fin) de la franja de la jornada."""
    return FRANJAS.get(jornada)


def obtener_dias_habiles():
    """Retorna los días hábiles disponibles para generación de horarios (lunes a viernes)."""
    return list(DIAS_HABILES)


def sesion_dentro_de_franja(jornada: Jornada, hora_inicio: time, hora_fin: time) -> bool:
    """Verifica si una sesión cabe dentro de la franja horaria de la jornada."""
    franja = FRANJAS.get(jornada)
    if not franja:
        return True
    inicio, fin = franja
    # Para nocturna, también se permite en el sábado
    if jornada == Jornada.NOCTURNA:
        sab_inicio, sab_fin = FRANJA_SABADO_NOCTURNA
        if hora_inicio >= sab_inicio and hora_fin <= sab_fin:
            return True
    return hora_inicio >= inicio and hora_fin <= fin


def texto_franja(jornada: Jornada) -> str:
    """Retorna texto legible de la franja horaria."""
    franja = FRANJAS.get(jornada)
    if not franja:
        return ""
    inicio, fin = franja
    texto = f"{inicio.strftime('%H:%M')} - {fin.strftime('%H:%M')}"
    if jornada == Jornada.NOCTURNA:
        sab_inicio, sab_fin = FRANJA_SABADO_NOCTURNA
        texto += f" (Sábado: {sab_inicio.strftime('%H:%M')} - {sab_fin.strftime('%H:%M')})"
    return texto


# ══════════════════════════════════════════════════════════════
# FUNCIONES DE VALIDACIÓN DE HORAS
# ══════════════════════════════════════════════════════════════

def calcular_horas_disponibles_semana(jornada: Jornada) -> float:
    """
    Calcula el total de horas disponibles en una semana para una jornada,
    incluyendo sábado para nocturna.
    """
    franja = FRANJAS.get(jornada)
    if not franja:
        return 0.0
    inicio, fin = franja
    horas_dia = fin.hour - inicio.hour
    total = horas_dia * len(DIAS_HABILES)
    if jornada == Jornada.NOCTURNA:
        sab_inicio, sab_fin = FRANJA_SABADO_NOCTURNA
        total += (sab_fin.hour - sab_inicio.hour)
    return float(total)


def calcular_horas_maximas_semanales(jornada: Jornada) -> float:
    """
    Calcula el máximo de horas semanales que una SOLA unidad puede ocupar,
    considerando el límite de MAX_HORAS_POR_SESION por día.
    """
    franja = FRANJAS.get(jornada)
    if not franja:
        return 0.0
    horas_efectivas_por_dia = min(franja[1].hour - franja[0].hour, MAX_HORAS_POR_SESION)
    dias = len(DIAS_HABILES)
    total = horas_efectivas_por_dia * dias
    if jornada == Jornada.NOCTURNA:
        total += min(FRANJA_SABADO_NOCTURNA[1].hour - FRANJA_SABADO_NOCTURNA[0].hour, MAX_HORAS_POR_SESION)
    return float(total)


def calcular_limite_horas_totales_malla(semanas: int) -> float:
    """
    Calcula el máximo de horas sincrónicas TOTALES que puede tener una malla,
    dado un número de semanas de periodo.

    Fórmula: LIMITE_SEMANAL × semanas
    Ejemplo: 20h × 8 semanas = 160h máximo total
    """
    if semanas <= 0:
        semanas = SEMANAS_REFERENCIA_MINIMA
    return float(LIMITE_HORAS_SINCRONICAS_SEMANALES_MALLA * semanas)


def calcular_horas_semanales_malla(total_horas_sincronicas: float, semanas: int) -> float:
    """
    Calcula cuántas horas sincrónicas semanales requiere una malla
    (suma de todas sus unidades dividida entre las semanas del periodo).
    """
    if semanas <= 0:
        semanas = SEMANAS_REFERENCIA_MINIMA
    return math.ceil(total_horas_sincronicas / semanas)


def validar_malla_cabe_en_horario(total_horas_sincronicas: float, semanas: int) -> dict:
    """
    Valida si el total de horas sincrónicas de una malla cabe dentro del
    límite semanal establecido (20h/semana).

    Args:
        total_horas_sincronicas: Suma de horas sincrónicas de todas las unidades de la malla
        semanas: Número de semanas del periodo (referencia)

    Returns:
        {"ok": True} si cabe
        {"ok": False, "motivo": str, "horas_semanales": float, "limite": int} si no cabe
    """
    if semanas <= 0:
        semanas = SEMANAS_REFERENCIA_MINIMA

    horas_semanales = math.ceil(total_horas_sincronicas / semanas)
    limite = LIMITE_HORAS_SINCRONICAS_SEMANALES_MALLA

    if horas_semanales <= limite:
        return {"ok": True, "horas_semanales": horas_semanales, "limite": limite}

    return {
        "ok": False,
        "motivo": (
            f"La malla requiere {horas_semanales}h sincrónicas semanales "
            f"y el máximo permitido es {limite}h "
            f"(con {semanas} semanas de periodo)"
        ),
        "horas_semanales": horas_semanales,
        "limite": limite,
    }


def validar_horas_semanales_unidad(horas_semanales: float, jornada: Jornada) -> dict:
    """
    Valida si las horas sincrónicas semanales de una unidad individual caben
    dentro de la franja de la jornada.
    """
    maximo = calcular_horas_maximas_semanales(jornada)
    if horas_semanales <= maximo:
        return {"ok": True}
    return {
        "ok": False,
        "motivo": (
            f"Las horas sincrónicas semanales ({horas_semanales}h) exceden "
            f"el máximo disponible ({maximo}h) para la jornada {jornada.value}"
        ),
        "maximo": maximo,
    }
