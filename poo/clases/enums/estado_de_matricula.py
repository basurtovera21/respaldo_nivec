# estado_de_matricula.py
from enum import Enum

class EstadoDeMatricula(Enum):
    MATRICULADO = "Matriculado" # Estado inicial al registrar
    RETIRADO = "Retirado"       # Estado tras solicitar_retiro()
    ANULADO = "Anulado"         # Estado tras anular_matricula()