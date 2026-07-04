#Enums
from poo.clases.enums.jornada import Jornada
from poo.clases.enums.registro_de_cupo import RegistroDeCupo
from poo.clases.enums.estado_de_matricula import EstadoDeMatricula

#Herencia
from poo.clases.usuarios.usuario_academico import UsuarioAcademico


class Estudiante(UsuarioAcademico):
    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, identificador_institucional: str, numero_de_matricula: str, jornada: Jornada, registro_de_cupo: RegistroDeCupo, carrera_registrada, campus_registrado, estado_de_matricula, **kwargs):
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
            identificador_institucional = identificador_institucional,
            **kwargs
        )
        self._numero_de_matricula = numero_de_matricula
        self._jornada = jornada #Instancia de Enum
        self._registro_de_cupo = registro_de_cupo #Instancia de Enum
        self._carrera_registrada = carrera_registrada
        self._campus_registrado = campus_registrado
        self._estado_de_matricula = EstadoDeMatricula.MATRICULADO #Instancia de Enum

    # --- Propiedades (encapsulación) ---

    @property
    def numero_de_matricula(self):
        return self._numero_de_matricula

    @property
    def jornada(self):
        return self._jornada

    @property
    def registro_de_cupo(self):
        return self._registro_de_cupo

    @property
    def carrera_registrada(self):
        return self._carrera_registrada

    @property
    def campus_registrado(self):
        return self._campus_registrado

    @property
    def estado_de_matricula(self):
        return self._estado_de_matricula

    # --- Métodos de validación ---

    def validar_datos_de_registro(self) -> dict:
        errores = {}
        if not self._jornada:
            errores["jornada"] = "Información requerida"
        if not self._registro_de_cupo:
            errores["registro_de_cupo"] = "Información requerida"
        if not self._carrera_registrada:
            errores["carrera_registrada"] = "Información requerida"
        return errores

    # --- Métodos de negocio ---

    def iniciar_sesion(self):
        if self._estado_de_matricula in (EstadoDeMatricula.RETIRADO, EstadoDeMatricula.ANULADO):
            return False
        return True
    
    def formalizar_matricula(self):
        self._estado_de_matricula = EstadoDeMatricula.MATRICULADO
    
    def anular_matricula(self):
        self._estado_de_matricula = EstadoDeMatricula.ANULADO
            
    def solicitar_retiro(self):
        if self._estado_de_matricula == EstadoDeMatricula.MATRICULADO:
            self._estado_de_matricula = EstadoDeMatricula.RETIRADO
            return True
        return False
