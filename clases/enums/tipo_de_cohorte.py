#Cohorte de matrícula
from enum import Enum


class TipoDeCohorte(Enum):
    PRIMERA_MATRICULA = "Primera matrícula"
    SEGUNDA_MATRICULA = "Segunda matrícula"
    EXONERACION = "Exoneración"