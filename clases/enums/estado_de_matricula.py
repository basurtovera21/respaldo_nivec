#Estudiante
from enum import Enum


class EstadoDeMatricula(Enum):
    ASPIRANTE = "Aspirante" #No formalizado
    PENDIENTE_DE_PAGO = "Pendiente de pago" #Pérdida de gratuidad
    MATRICULADO = "Matriculado" #Formalizado
    RETIRADO = "Retirado" #Procesado por solicitar_retiro()
    ANULADO = "Anulada"