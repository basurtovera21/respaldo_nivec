#Docente
from enum import Enum


class TipoDeVinculacion(Enum):
    NOMBRAMIENTO = "Nombramiento"
    CONTRATO = "Contrato"
    OCASIONAL = "Ocasional"
    HONORARIO = "Honorario"