#Enum
from clases.enums.perfil_administrativo import PerfilAdministrativo

#Herencia
from clases.usuarios.usuario_de_sistema import UsuarioDeSistema


class UsuarioAdministrativo(UsuarioDeSistema):
    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, identificador_administrativo: str, perfil_administrativo: PerfilAdministrativo, **kwargs):
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
            **kwargs
        )
        self.identificador_administrativo = identificador_administrativo
        self.perfil_administrativo = perfil_administrativo #Instancia
   
        
    def iniciar_sesion(self): #Sobreescritura
        return True