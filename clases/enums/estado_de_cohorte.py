#Tonyfrom enum import Enum
from enum import Enum

class EstadoDeCohorte(Enum):
    ABIERTA = "Abierta"
    CERRADA = "Cerrada"
    EN_PROCESO = "En proceso"
    FINALIZADA = "Finalizada"