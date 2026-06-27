from datetime import date
from poo.clases.enums.modalidad import Modalidad

class Carrera:
    def __init__(self, codigo_de_carrera: str, nombre: str, modalidad: Modalidad, facultad: str, vigencia_sniese: date):
        self.codigo_de_carrera = codigo_de_carrera
        self.nombre = nombre
        self.modalidad = modalidad
        self.facultad = facultad
        self.vigencia_sniese = vigencia_sniese

    @staticmethod
    def normalizar_nombre(nombre):
        return str(nombre or "").strip().lower()

    def esta_activa(self):
        return date.today() <= self.vigencia_sniese
