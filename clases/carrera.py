<<<<<<< Updated upstream
=======
from datetime import date

# Enum
from clases.enums.modalidad import Modalidad


class Carrera:
    def __init__(
        self,
        codigo_de_carrera: str,
        nombre: str,
        modalidad: Modalidad,
        campo_de_conocimiento: str,
        vigencia_sniese: date,
    ):
        self.codigo_de_carrera = codigo_de_carrera
        self.nombre = nombre
        self.modalidad = modalidad  # Instancia
        self.campo_de_conocimiento = campo_de_conocimiento
        self.vigencia_sniese = vigencia_sniese

    def esta_activa(self):  # Retorna bool
        # True si la fecha actual no supera la vigencia_sniese.
        fecha_actual = date.today()

        if fecha_actual <= self.vigencia_sniese:
            return True
        else:
            return False
>>>>>>> Stashed changes
