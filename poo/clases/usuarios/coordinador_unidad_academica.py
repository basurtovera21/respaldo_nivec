#Herencia múltiple
from poo.clases.usuarios.usuario_administrativo import UsuarioAdministrativo
from poo.clases.usuarios.docente import Docente
from poo.clases.universidad import Universidad

class CoordinadorUnidadAcademica(UsuarioAdministrativo, Docente):
    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, identificador_administrativo: str, perfil_administrativo, identificador_institucional: str, tipo_de_vinculacion, tiempo_de_dedicacion, carga_horaria_maxima: float, identificador_coordinador_ua: str, unidad_academica: str, universidad: Universidad = None, **kwargs):
        
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
            identificador_institucional = identificador_institucional,
            tipo_de_vinculacion = tipo_de_vinculacion,
            tiempo_de_dedicacion = tiempo_de_dedicacion,
            carga_horaria_maxima = carga_horaria_maxima,
            universidad = universidad,
            **kwargs
        )
        self.identificador_coordinador_ua = identificador_coordinador_ua
        self.unidad_academica = unidad_academica
        
    def iniciar_sesion(self):
        return True