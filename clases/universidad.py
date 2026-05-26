class Universidad:
    def __init__(
        self,
        nombre: str,
        abreviatura: str,
        codigo_sniese: str,
        direccion_matriz: str,
        identificador_visual: str,
    ):
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.codigo_sniese = codigo_sniese
        self.direccion_matriz = direccion_matriz
        self.identificador_visual = identificador_visual  # (ruta de archivo)


    def recuperar_informacion_institucional(self):  # Retorna dict
        pass
