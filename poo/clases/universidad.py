import unicodedata


class Universidad:
    def __init__(self, nombre: str, abreviatura: str, codigo_sniese: str, direccion_matriz: str = ""):
        self._nombre = nombre
        self._abreviatura = abreviatura
        self._codigo_sniese = codigo_sniese
        self._direccion_matriz = direccion_matriz

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = valor

    @property
    def abreviatura(self):
        return self._abreviatura

    @abreviatura.setter
    def abreviatura(self, valor):
        self._abreviatura = valor

    @property
    def codigo_sniese(self):
        return self._codigo_sniese

    @property
    def direccion_matriz(self):
        return self._direccion_matriz

    @direccion_matriz.setter
    def direccion_matriz(self, valor):
        self._direccion_matriz = valor

    @staticmethod
    def normalizar_texto(texto: str) -> str:
        if not texto:
            return ""
        texto = str(texto).strip().lower()
        texto = ''.join(
            caracter for caracter in unicodedata.normalize('NFD', texto)
            if unicodedata.category(caracter) != 'Mn'
        )
        return texto

    def validar_datos_de_registro(self) -> dict:
        errores = {}
        if not self._nombre or not str(self._nombre).strip():
            errores["nombre"] = "Información requerida"
        if not self._abreviatura or not str(self._abreviatura).strip():
            errores["abreviatura"] = "Información requerida"
        if not self._codigo_sniese or not str(self._codigo_sniese).strip():
            errores["codigo_sniese"] = "Información requerida"
        return errores

    def validar_codigo_sniese_unico(self, codigos_existentes: set) -> bool:
        codigo_normalizado = Universidad.normalizar_texto(self._codigo_sniese)
        return codigo_normalizado not in codigos_existentes

    def __str__(self):
        return f"{self._nombre} ({self._abreviatura})"
