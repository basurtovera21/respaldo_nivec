import unicodedata
from datetime import date


class Carrera:
    def __init__(self, codigo_de_carrera: str, nombre: str, vigencia_sniese: date = None):
        self._codigo_de_carrera = codigo_de_carrera
        self._nombre = nombre
        self._vigencia_sniese = vigencia_sniese

    @property
    def codigo_de_carrera(self):
        return self._codigo_de_carrera

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = valor

    @property
    def vigencia_sniese(self):
        return self._vigencia_sniese

    @staticmethod
    def normalizar_nombre(nombre: str) -> str:
        if not nombre:
            return ""
        texto = str(nombre).strip().lower()
        texto = ''.join(
            caracter for caracter in unicodedata.normalize('NFD', texto)
            if unicodedata.category(caracter) != 'Mn'
        )
        return texto

    def validar_datos_de_registro(self) -> dict:
        errores = {}
        if not self._nombre or not str(self._nombre).strip():
            errores["nombre"] = "Información requerida"
        if not self._vigencia_sniese:
            errores["vigencia_sniese"] = "Información requerida"
        return errores

    def esta_activa(self) -> bool:
        if not self._vigencia_sniese:
            return False
        return date.today() <= self._vigencia_sniese

    def es_registro_duplicado(self, nombres_existentes: set) -> bool:
        nombre_normalizado = self.__class__.normalizar_nombre(self._nombre)
        return nombre_normalizado in nombres_existentes
