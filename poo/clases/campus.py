class Campus:
    def __init__(self, codigo_de_campus: str, nombre: str, direccion_fisica: str, provincia: str):
        self.codigo_de_campus = codigo_de_campus
        self.nombre = nombre
        self.direccion_fisica = direccion_fisica
        self.provincia = provincia

    @staticmethod
    def normalizar_nombre(nombre):
        return str(nombre or "").strip().lower()

    def es_nombre_equivalente(self, otro_nombre):
        return Campus.normalizar_nombre(self.nombre) == Campus.normalizar_nombre(otro_nombre)

    def validar_datos_de_registro(self):
        errores = {}

        if not self.nombre or not str(self.nombre).strip():
            errores["nombre"] = "Información requerida"

        if not self.direccion_fisica or not str(self.direccion_fisica).strip():
            errores["direccion_fisica"] = "Información requerida"

        if not self.provincia or not str(self.provincia).strip():
            errores["provincia"] = "Información requerida"

        return errores
