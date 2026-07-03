from poo.clases.usuarios.usuario_administrativo import UsuarioAdministrativo
from poo.clases.enums.perfil_administrativo import PerfilAdministrativo


class CoordinadorUnidadAcademica(UsuarioAdministrativo):
    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, identificador_administrativo: str, identificador_coordinador_ua: str, carrera_asignada=None, tiempo_de_dedicacion=None, carga_horaria_maxima: float = 0.0, tipo_de_vinculacion=None, universidad=None, **kwargs):

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
            perfil_administrativo=PerfilAdministrativo.COORDINADOR_UA,
            universidad=universidad,
            **kwargs
        )
        self._identificador_coordinador_ua = identificador_coordinador_ua
        self._carrera_asignada = carrera_asignada
        self._tiempo_de_dedicacion = tiempo_de_dedicacion
        self._carga_horaria_maxima = carga_horaria_maxima
        self._tipo_de_vinculacion = tipo_de_vinculacion

    @property
    def identificador_coordinador_ua(self):
        return self._identificador_coordinador_ua

    @property
    def carrera_asignada(self):
        return self._carrera_asignada

    @property
    def tiempo_de_dedicacion(self):
        return self._tiempo_de_dedicacion

    @property
    def carga_horaria_maxima(self):
        return self._carga_horaria_maxima

    @property
    def tipo_de_vinculacion(self):
        return self._tipo_de_vinculacion

    def iniciar_sesion(self):
        return True

    def puede_ser_modificado_o_eliminado(self) -> bool:
        return True

    def validar_datos_de_registro(self) -> dict:
        errores = {}
        if not self._carrera_asignada:
            errores["carrera_asignada"] = "Información requerida"
        if not self._tiempo_de_dedicacion:
            errores["tiempo_de_dedicacion"] = "Información requerida"
        if self._carga_horaria_maxima is None:
            errores["carga_horaria_maxima"] = "Información requerida"
        elif self._carga_horaria_maxima < 0:
            errores["carga_horaria_maxima"] = "Registro no válido"
        return errores
