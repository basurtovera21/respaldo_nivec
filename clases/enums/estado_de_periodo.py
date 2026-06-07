#Periodo de nivelación
from enum import Enum


class EstadoDePeriodo(Enum):
    PLANIFICACION = "Planificación"
    EN_CURSO = "En curso"
    EVALUACION = "Evaluación"
    CERRADO = "Cerrado"
