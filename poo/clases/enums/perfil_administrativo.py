#Usuario administrativo
from enum import Enum


class PerfilAdministrativo(Enum):
    RECTOR = "Rector"
    VICERRECTOR_ACADEMICO = "Vicerrector académico"
    DIRECTOR_DAN = "Director de dirección de admisión y nivelación"
    COORDINADOR_DAN = "Coordinador de dirección de admisión y nivelación"
    COORDINADOR_UA = "Coordinador de unidad académica"