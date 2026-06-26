class Universidad:
    def __init__(self, nombre: str, abreviatura: str, codigo_sniese: str, direccion_matriz: str, identificador_visual: str = None):
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.codigo_sniese = codigo_sniese
        self.direccion_matriz = direccion_matriz
        self.identificador_visual = identificador_visual

    def validar_datos_de_registro(self):
        errores = {}
        if not self.nombre or not str(self.nombre).strip():
            errores["nombre"] = "Información requerida"
        if not self.abreviatura or not str(self.abreviatura).strip():
            errores["abreviatura"] = "Información requerida"
        if not self.codigo_sniese or not str(self.codigo_sniese).strip():
            errores["codigo_sniese"] = "Información requerida"
        if not self.direccion_matriz or not str(self.direccion_matriz).strip():
            errores["direccion_matriz"] = "Información requerida"
        return errores