#Enums
from poo.clases.enums.tipo_de_identificacion import TipoDeIdentificacion
from poo.clases.enums.estado_de_usuario import EstadoDeUsuario

#Clase abstracta
from abc import ABCMeta
from abc import abstractmethod


class UsuarioDeSistema(metaclass=ABCMeta):
    _MINIMO_CARACTERES_CONTRASENA = 8
    _MAXIMO_CARACTERES_CONTRASENA = 16

    def __init__(self, tipo_de_identificacion: TipoDeIdentificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, **kwargs):
        self._tipo_de_identificacion = tipo_de_identificacion
        self._identificacion = identificacion
        self._nombres = nombres
        self._apellidos = apellidos
        self._correo_institucional = correo_institucional
        self.contrasena = contrasena
        self._fecha_de_nacimiento = fecha_de_nacimiento
        self._sexo = sexo
        self._etnia = etnia
        self._porcentaje_de_discapacidad = porcentaje_de_discapacidad
        self._celular = celular
        self._direccion = direccion
        self._estado_de_usuario = EstadoDeUsuario.PENDIENTE
        super().__init__()


    @property
    def tipo_de_identificacion(self):
        return self._tipo_de_identificacion

    @property
    def identificacion(self):
        return self._identificacion

    @property
    def nombres(self):
        return self._nombres

    @nombres.setter
    def nombres(self, valor):
        self._nombres = valor

    @property
    def apellidos(self):
        return self._apellidos

    @apellidos.setter
    def apellidos(self, valor):
        self._apellidos = valor

    @property
    def correo_institucional(self):
        return self._correo_institucional

    @property
    def estado_de_usuario(self):
        return self._estado_de_usuario

    @property
    def contrasena(self):
        return self.__contrasena

    @contrasena.setter
    def contrasena(self, nueva_contrasena):
        UsuarioDeSistema.validar_contrasena(nueva_contrasena)
        self.__contrasena = nueva_contrasena

    @abstractmethod
    def iniciar_sesion(self):
        pass

    def puede_iniciar_sesion(self) -> bool:
        return self._estado_de_usuario == EstadoDeUsuario.ACTIVO

    def esta_activo(self) -> bool:
        return self._estado_de_usuario == EstadoDeUsuario.ACTIVO

    def esta_bloqueado(self) -> bool:
        return self._estado_de_usuario == EstadoDeUsuario.BLOQUEADO

    def esta_inactivo(self) -> bool:
        return self._estado_de_usuario == EstadoDeUsuario.INACTIVO

    def esta_pendiente(self) -> bool:
        return self._estado_de_usuario == EstadoDeUsuario.PENDIENTE

    def activar(self):
        self._estado_de_usuario = EstadoDeUsuario.ACTIVO

    def inactivar(self):
        self._estado_de_usuario = EstadoDeUsuario.INACTIVO

    def bloquear(self):
        self._estado_de_usuario = EstadoDeUsuario.BLOQUEADO

    @staticmethod
    def validar_estado_de_usuario(estado_de_usuario_actual: str) -> bool:
        return estado_de_usuario_actual == EstadoDeUsuario.ACTIVO.value

    @staticmethod
    def validar_contrasena(nueva_contrasena: str, confirmar_contrasena: str = None):
        if confirmar_contrasena is not None and nueva_contrasena != confirmar_contrasena:
            raise ValueError("Las contraseñas registradas no coinciden")

        if len(nueva_contrasena) < UsuarioDeSistema._MINIMO_CARACTERES_CONTRASENA:
            raise ValueError(f"La contraseña debe contener un mínimo de {UsuarioDeSistema._MINIMO_CARACTERES_CONTRASENA} caracteres")

        if len(nueva_contrasena) > UsuarioDeSistema._MAXIMO_CARACTERES_CONTRASENA:
            raise ValueError(f"La contraseña debe contener un máximo de {UsuarioDeSistema._MAXIMO_CARACTERES_CONTRASENA} caracteres")

        return True