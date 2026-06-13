from datetime import date

#Enum
from poo.clases.enums.modalidad import Modalidad


class Carrera:
    def __init__(self, codigo_de_carrera: str, nombre: str, modalidad: Modalidad, campo_de_conocimiento: str, vigencia_sniese: date):
        self.codigo_de_carrera = codigo_de_carrera
        self.nombre = nombre
        self.modalidad = modalidad #Enum
        self.campo_de_conocimiento = campo_de_conocimiento
        self.vigencia_sniese = vigencia_sniese
        

    def esta_activa(self) -> bool:
        return date.today() <= self.vigencia_sniese