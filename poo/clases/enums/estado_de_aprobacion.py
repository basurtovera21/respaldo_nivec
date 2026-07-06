from enum import Enum


class EstadoDeAprobacion(Enum):
    PENDIENTE = "Pendiente"
    APROBADO = "Aprobado"
    REPROBADO = "Reprobado"
    RETIRADO = "Retirado"
    ANULADO = "Anulado"