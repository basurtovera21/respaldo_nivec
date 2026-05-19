#Enums
from clases.enums.tipo_de_identificacion import TipoDeIdentificacion
from clases.enums.estado_de_usuario import EstadoDeUsuario

#Clase abstracta
from abc import ABCMeta
from abc import abstractmethod


class UsuarioDeSistema (metaclass = ABCMeta):
    minimo_de_caracteres_contrasena = 8 #Referencial
    maximo_de_caracteres_contrasena = 16 #Referencial
    def __init__(self, tipo_de_identificacion: TipoDeIdentificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento: str, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, **kwargs): #Aceptar argumentos adicionales (para herencia múltiple)
        self.tipo_de_identificacion = tipo_de_identificacion #Instancia
        self._identificacion = identificacion
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo_institucional = correo_institucional
        self.__contrasena = contrasena 
        self.fecha_de_nacimiento = fecha_de_nacimiento #datetime.time
        self.sexo = sexo
        self.etnia = etnia
        self.porcentaje_de_discapacidad = porcentaje_de_discapacidad #(0.0 -100.0)
        self._celular = celular
        self._direccion = direccion
        self._estado_de_usuario = EstadoDeUsuario.PENDIENTE #No es parámetro de __init__ (valor interno)
        super().__init__(**kwargs) 
    
    
    @abstractmethod
    def iniciar_sesion(self):
        pass
    
    def cerrar_sesion(self):
        pass
    
    @property
    def contrasena(self):
        return self.__contrasena
    
    @contrasena.setter
    def contrasena(self, nueva_contrasena):
        if len(nueva_contrasena) < self.minimo_de_caracteres_contrasena:
            print(f"Contraseña no válida (mínimo {self.minimo_de_caracteres_contrasena} caracteres).")
        elif len(nueva_contrasena) > self.maximo_de_caracteres_contrasena:
            print(f"Contraseña no válida (máximo {self.maximo_de_caracteres_contrasena} caracteres).")
        else:
            self.__contrasena = nueva_contrasena
            print("Registro válido, la contraseña ha sido cambiada.")
            
    def recuperar_contrasena(self):
        pass
    
    def confirmar_cambio_de_contrasena(self):
        pass