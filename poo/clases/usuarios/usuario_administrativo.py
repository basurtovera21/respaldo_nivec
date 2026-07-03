from poo.clases.enums.perfil_administrativo import PerfilAdministrativo
from poo.clases.usuarios.usuario_de_sistema import UsuarioDeSistema
from poo.clases.universidad import Universidad


class UsuarioAdministrativo(UsuarioDeSistema):
    _PERFILES_NO_MODIFICABLES = (PerfilAdministrativo.DIRECTOR_DAN,)

    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, identificador_administrativo: str, perfil_administrativo: PerfilAdministrativo, universidad: Universidad = None, **kwargs):
        
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
            universidad=universidad,
            **kwargs
        )
        self._universidad = universidad
        self._identificador_administrativo = identificador_administrativo
        self._perfil_administrativo = perfil_administrativo

    @property
    def universidad(self):
        return self._universidad

    @property
    def identificador_administrativo(self):
        return self._identificador_administrativo

    @property
    def perfil_administrativo(self):
        return self._perfil_administrativo

    def iniciar_sesion(self):
        return True

    def puede_ser_modificado_o_eliminado(self) -> bool:
        return self._perfil_administrativo not in self._PERFILES_NO_MODIFICABLES

    @staticmethod
    def definir_prefijo_identificador(perfil: PerfilAdministrativo) -> str:
        mapeo_prefijos = {
            PerfilAdministrativo.RECTOR: "AD",
            PerfilAdministrativo.VICERRECTOR_ACADEMICO: "AD",
            PerfilAdministrativo.DIRECTOR_DAN: "DAN",
            PerfilAdministrativo.COORDINADOR_DAN: "CAN",
            PerfilAdministrativo.COORDINADOR_UA: "CUA",
        }
        return mapeo_prefijos.get(perfil, "AD")

    @staticmethod
    def validar_perfil_administrativo(valor_perfil: str, perfiles_permitidos: list) -> bool:
        valor_normalizado = str(valor_perfil).strip().lower()
        perfiles_normalizados = {str(p.value).strip().lower() for p in perfiles_permitidos}
        return valor_normalizado in perfiles_normalizados

    @staticmethod
    def obtener_perfil_exacto(valor_perfil: str, perfiles_permitidos: list):
        valor_normalizado = str(valor_perfil).strip().lower()
        for perfil in perfiles_permitidos:
            if str(perfil.value).strip().lower() == valor_normalizado:
                return perfil.value
        return None

    def validar_datos_de_registro(self) -> dict:
        errores = {}
        if not self._perfil_administrativo:
            errores["perfil_administrativo"] = "Información requerida"
        return errores
