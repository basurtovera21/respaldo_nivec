#Usuario de sistema
from enum import Enum


class EstadoDeUsuario(Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    BLOQUEADO = "Bloqueado"
    PENDIENTE = "Pendiente"