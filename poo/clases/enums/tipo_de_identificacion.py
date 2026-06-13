#Usuario de sistema
from enum import Enum


class TipoDeIdentificacion(Enum):
    CEDULA = "Cédula"
    PASAPORTE = "Pasaporte"
    CEDULA_EXTRANJERA = "Cédula extranjera"