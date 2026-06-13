#Estudiante
from enum import Enum


class EstadoDeMatricula(Enum):
    ASPIRANTE = "Aspirante" #No formalizado
    PENDIENTE_DE_PAGO = "Pendiente de pago" #Pérdida de gratuidad
    MATRICULADO = "Matriculado" #Formalizado
    RETIRADO = "Retirada" #Procesado por solicitar_retiro()
    ANULADO = "Anulada"