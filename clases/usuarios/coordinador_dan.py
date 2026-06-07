#Herencia
from clases.usuarios.usuario_administrativo import UsuarioAdministrativo


class CoordinadorDAN(UsuarioAdministrativo):
    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, identificador_administrativo: str, perfil_administrativo, identificador_coordinador_dan: str, **kwargs):
        super().__init__(
            tipo_de_identificacion = tipo_de_identificacion,
            identificacion = identificacion,
            nombres = nombres,
            apellidos = apellidos,
            correo_institucional = correo_institucional,
            contrasena = contrasena,
            fecha_de_nacimiento = fecha_de_nacimiento,
            sexo = sexo,
            etnia = etnia,
            porcentaje_de_discapacidad = porcentaje_de_discapacidad,
            celular = celular,
            direccion = direccion,
            identificador_administrativo = identificador_administrativo,
            perfil_administrativo = perfil_administrativo,
            **kwargs
            )
        self.identificador_coordinador_dan = identificador_coordinador_dan
        
        
    def iniciar_sesion(self): #Sobreescritura
        return True