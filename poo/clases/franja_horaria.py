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



# ══════════════════════════════════════════════════════════════
# FUNCIONES DE GENERACIÓN AUTOMÁTICA DE HORARIOS
# ══════════════════════════════════════════════════════════════

def distribucion_simetrica(horas: float, max_dias: int = 5, min_h: int = 1, max_h: int = 3) -> list:
    """
    Reparte un total de horas en bloques de HORAS ENTERAS lo más iguales posible,
    uno por día, cada bloque entre min_h y max_h, usando hasta max_dias días.

    Algoritmo:
        1. Redondea horas al entero más cercano
        2. Calcula cuántos días se necesitan (min para cubrir con max_h por día)
        3. Distribuye equitativamente con un bloque extra para los primeros días

    Args:
        horas: Total de horas a distribuir
        max_dias: Máximo de días disponibles (default: 5, lunes a viernes)
        min_h: Mínimo de horas por sesión (default: 1)
        max_h: Máximo de horas por sesión (default: 3)

    Returns:
        Lista de enteros representando horas por día (ej: [2, 2, 1] para 5h en 3 días)
    """
    h = int(round(horas))
    if h < min_h:
        return []
    dias = min(max_dias, h)
    dias = max(dias, math.ceil(h / max_h))
    dias = min(dias, max_dias)
    dias = max(dias, 1)
    base = h // dias
    extra = h % dias
    return [min(base + (1 if i < extra else 0), max_h) for i in range(dias)]


def sugerir_bloque_libre(dia_poo, franja_inicio: time, franja_fin: time,
                          bloque_horas: int, ocupados: list):
    """
    Busca un bloque horario libre dentro de una franja para un día específico.

    Algoritmo:
        Recorre la franja en pasos de 1 hora buscando un slot donde el bloque
        no entre en conflicto con ningún horario ocupado.

    Args:
        dia_poo: Instancia de DiaDeSemana para el día buscado
        franja_inicio: Hora de inicio de la franja permitida
        franja_fin: Hora de fin de la franja permitida
        bloque_horas: Duración del bloque a ubicar (en horas)
        ocupados: Lista de instancias Horario que ya están reservadas

    Returns:
        Tupla (hora_inicio, hora_fin) del slot libre encontrado, o None si no hay espacio
    """
    from datetime import datetime, timedelta
    from poo.clases.horario import Horario as HorarioPOO

    base = datetime(2000, 1, 1, franja_inicio.hour, franja_inicio.minute)
    tope = datetime(2000, 1, 1, franja_fin.hour, franja_fin.minute)
    dur = timedelta(hours=bloque_horas)
    paso = timedelta(minutes=60)
    actual = base

    while actual + dur <= tope:
        h_ini = actual.time()
        h_fin = (actual + dur).time()
        candidato = HorarioPOO(
            dia_semana=dia_poo, hora_inicio=h_ini, hora_fin=h_fin,
            espacio_de_imparticion="",
        )
        if not any(candidato.verificar_conflicto_horario(o) for o in ocupados):
            return (h_ini, h_fin)
        actual += paso

    return None
