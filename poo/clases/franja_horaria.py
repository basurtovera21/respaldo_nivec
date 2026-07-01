from datetime import time

from poo.clases.enums.jornada import Jornada


# Duración mínima y máxima de una sesión (bloque) en un mismo día.
MIN_HORAS_POR_SESION = 1.0
MAX_HORAS_POR_SESION = 3.0

# Franja horaria permitida por jornada (patrón semanal). No cruzan medianoche
# para que la aritmética de solape sea trivial.
FRANJAS = {
    Jornada.MATUTINA: (time(7, 0), time(13, 0)),
    Jornada.VESPERTINA: (time(13, 0), time(19, 0)),
    Jornada.NOCTURNA: (time(19, 0), time(22, 0)),
}


def obtener_franja(jornada: Jornada):
    return FRANJAS.get(jornada)


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
