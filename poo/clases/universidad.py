class Universidad:
    def __init__(self, nombre: str, abreviatura: str, codigo_sniese: str, direccion_matriz: str = ""):
        self._nombre = nombre
        self._abreviatura = abreviatura
        self._codigo_sniese = codigo_sniese
        self._direccion_matriz = direccion_matriz

    # --- Propiedades ---

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

    # --- Validaciones ---

    def validar_datos_de_registro(self) -> dict:
        errores = {}
        if not self._nombre or not str(self._nombre).strip():
            errores["nombre"] = "Información requerida"
        if not self._abreviatura or not str(self._abreviatura).strip():
            errores["abreviatura"] = "Información requerida"
        if not self._codigo_sniese or not str(self._codigo_sniese).strip():
            errores["codigo_sniese"] = "Información requerida"
        return errores

    # --- Representación ---

    def obtener_nombre_completo(self) -> str:
        return f"{self._nombre} ({self._abreviatura})"

    def __str__(self):
        return self.obtener_nombre_completo()
