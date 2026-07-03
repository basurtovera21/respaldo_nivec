class Campus:
    def __init__(self, codigo_de_campus: str, nombre: str, direccion_fisica: str = "", provincia: str = ""):
        self._codigo_de_campus = codigo_de_campus
        self._nombre = nombre
        self._direccion_fisica = direccion_fisica
        self._provincia = provincia

    @property
    def codigo_de_campus(self):
        return self._codigo_de_campus

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = valor

    @property
    def direccion_fisica(self):
        return self._direccion_fisica

    @direccion_fisica.setter
    def direccion_fisica(self, valor):
        self._direccion_fisica = valor

    @property
    def provincia(self):
        return self._provincia

    @provincia.setter
    def provincia(self, valor):
        self._provincia = valor

    def validar_datos_de_registro(self) -> dict:
        errores = {}
        if not self._nombre or not str(self._nombre).strip():
            errores["nombre"] = "Información requerida"
        if not self._direccion_fisica or not str(self._direccion_fisica).strip():
            errores["direccion_fisica"] = "Información requerida"
        return errores

    def __str__(self):
        return self._nombre
