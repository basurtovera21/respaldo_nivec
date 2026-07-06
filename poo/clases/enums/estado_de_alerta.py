from enum import Enum


class EstadoDeAlerta(Enum):
    CRITICO = "Crítico: Plazo vencido"
    PREVENTIVO = "Preventivo: Próximo a vencer"
    NORMAL = "Normal: Dentro del plazo"