class UsuarioDeSistema:
    def __init__(self, tipo_de_identificacion, identificacion, nombres, apellidos, correo, contrasena, fecha_de_nacimiento, sexo, etnia, porcentaje_de_discapacidad, celular, direccion, estado, **kwargs):
        self._tipo_de_identificacion = tipo_de_identificacion
        self._identificacion = identificacion
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.__contrasena = contrasena 
        self._fecha_de_nacimiento = fecha_de_nacimiento
        self._sexo = sexo
        self._etnia = etnia
        self._porcentaje_de_discapacidad = porcentaje_de_discapacidad 
        self._celular = celular
        self._direccion = direccion
        self.estado = estado
    
    
    def iniciar_sesion(self):
        pass
    def cerrar_sesion(self):
        pass
    def recuperar_contrasena(self):
        pass