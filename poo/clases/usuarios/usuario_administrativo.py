from poo.clases.enums.perfil_administrativo import PerfilAdministrativo
from poo.clases.usuarios.usuario_de_sistema import UsuarioDeSistema
from poo.clases.universidad import Universidad 

class UsuarioAdministrativo(UsuarioDeSistema):
    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, identificador_administrativo: str, perfil_administrativo: PerfilAdministrativo, universidad: Universidad = None, **kwargs):
        
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
            # Se reenvía 'universidad' para la herencia múltiple (CoordinadorUnidadAcademica),
            # donde Docente también la requiere. En herencia simple, la clase base la ignora.
            universidad = universidad,
            **kwargs
        )
        self.universidad = universidad
        self.identificador_administrativo = identificador_administrativo
        self.perfil_administrativo = perfil_administrativo
        
    def iniciar_sesion(self):
        return True
      
    def puede_ser_modificado_o_eliminado(self):
        if self.perfil_administrativo == PerfilAdministrativo.DIRECTOR_DAN:
            return False
        return True

    @staticmethod
    def definir_prefijo_identificador(perfil: PerfilAdministrativo):
        mapeo_prefijos = {
            PerfilAdministrativo.RECTOR: "AD",
            PerfilAdministrativo.VICERRECTOR_ACADEMICO: "AD",
            PerfilAdministrativo.DIRECTOR_DAN: "DAN",
            PerfilAdministrativo.COORDINADOR_DAN: "CAN",
            PerfilAdministrativo.COORDINADOR_UA: "CUA",
        }
        return mapeo_prefijos.get(perfil, "AD")