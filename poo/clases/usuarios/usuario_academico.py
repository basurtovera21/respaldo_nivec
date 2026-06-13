#Herencia
from poo.clases.usuarios.usuario_de_sistema import UsuarioDeSistema


class UsuarioAcademico(UsuarioDeSistema):
    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, identificador_institucional: str, **kwargs):
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
            **kwargs #Recibir argumentos adicionales
        )
        self.identificador_institucional = identificador_institucional
        
        
    def iniciar_sesion(self):
        return True
        
        
    def obtener_registro_institucional(self):
        return {
            "Identificador institucional": self.identificador_institucional,
            "Nombres": self.nombres,
            "Apellidos": self.apellidos,
            "Correo institucional": self.correo_institucional,
        }