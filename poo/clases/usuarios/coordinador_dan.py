from poo.clases.usuarios.usuario_administrativo import UsuarioAdministrativo
from poo.clases.enums.perfil_administrativo import PerfilAdministrativo


class CoordinadorDAN(UsuarioAdministrativo):
    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, identificador_administrativo: str, identificador_coordinador_dan: str, universidad=None, **kwargs):
        
        super().__init__(
            tipo_de_identificacion=tipo_de_identificacion,
            identificacion=identificacion,
            nombres=nombres,
            apellidos=apellidos,
            correo_institucional=correo_institucional,
            contrasena=contrasena,
            fecha_de_nacimiento=fecha_de_nacimiento,
            sexo=sexo,
            etnia=etnia,
            porcentaje_de_discapacidad=porcentaje_de_discapacidad,
            celular=celular,
            direccion=direccion,
            identificador_administrativo=identificador_administrativo,
            perfil_administrativo=PerfilAdministrativo.COORDINADOR_DAN,
            universidad=universidad,
            **kwargs
        )
        self._identificador_coordinador_dan = identificador_coordinador_dan

    @property
    def identificador_coordinador_dan(self):
        return self._identificador_coordinador_dan

    def iniciar_sesion(self):
        return True

    def puede_ser_modificado_o_eliminado(self) -> bool:
        return True
