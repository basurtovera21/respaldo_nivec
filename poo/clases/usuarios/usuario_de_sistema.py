#Enums
from poo.clases.enums.tipo_de_identificacion import TipoDeIdentificacion
from poo.clases.enums.estado_de_usuario import EstadoDeUsuario

#Clase abstracta
from abc import ABCMeta
from abc import abstractmethod


class UsuarioDeSistema (metaclass = ABCMeta):
    minimo_de_caracteres_contrasena = 8 #Referencia
    maximo_de_caracteres_contrasena = 16 #Referencia
    
    def __init__(self, tipo_de_identificacion: TipoDeIdentificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, **kwargs): #Aceptar argumentos adicionales (para herencia múltiple)
        self.tipo_de_identificacion = tipo_de_identificacion #Instancia
        self._identificacion = identificacion
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo_institucional = correo_institucional
        self.contrasena = contrasena #El setter valida longitud desde la creación
        self.fecha_de_nacimiento = fecha_de_nacimiento #datetime.time
        self.sexo = sexo
        self.etnia = etnia
        self.porcentaje_de_discapacidad = porcentaje_de_discapacidad #(0.0 - 100.0)
        self._celular = celular
        self._direccion = direccion
        self._estado_de_usuario = EstadoDeUsuario.PENDIENTE
        # Clase base del dominio: ignora kwargs sobrantes para no romper la
        # herencia cooperativa (object no acepta argumentos).
        super().__init__()
    
    
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
    
    #Iniciar sesión
    @staticmethod
    def validar_estado_de_usuario(estado_de_usuario_actual: str):
        if estado_de_usuario_actual == EstadoDeUsuario.ACTIVO.value:
            return True, ""
        elif estado_de_usuario_actual == EstadoDeUsuario.BLOQUEADO.value:
            return False, "El usuario ha sido bloqueado indefinidamente"
        elif estado_de_usuario_actual == EstadoDeUsuario.INACTIVO.value:
            return False, "El usuario se encuentra inactivo actualmente"
        elif estado_de_usuario_actual == EstadoDeUsuario.PENDIENTE.value:
            return False, "El usuario está pendiente de activación"
        else:
            return False, "Estado no reconocido"
    
    #Cambiar contraseña
    @staticmethod
    def validar_contrasena(nueva_contrasena: str, confirmar_contrasena: str = None):
        if confirmar_contrasena is not None and nueva_contrasena != confirmar_contrasena:
            raise ValueError("Las contraseñas registradas no coinciden")
            
        if len(nueva_contrasena) < UsuarioDeSistema.minimo_de_caracteres_contrasena:
            raise ValueError(f"mínimo {UsuarioDeSistema.minimo_de_caracteres_contrasena} caracteres")
            
        if len(nueva_contrasena) > UsuarioDeSistema.maximo_de_caracteres_contrasena:
            raise ValueError(f"máximo {UsuarioDeSistema.maximo_de_caracteres_contrasena} caracteres")
            
        return True