#Enums
from clases.enums.jornada import Jornada
from clases.enums.registro_de_cupo import RegistroDeCupo
from clases.enums.estado_de_matricula import EstadoDeMatricula

#Herencia
from clases.usuarios.usuario_academico import UsuarioAcademico


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
        self.numero_de_matricula = numero_de_matricula
        self.jornada = jornada #Instancia
        self.registro_de_cupo = registro_de_cupo #Instancia
        self.carrera_registrada = carrera_registrada
        self.campus_registrado = campus_registrado
        self._estado_de_matricula = estado_de_matricula #Instancia
     
     
    def iniciar_sesion(self): #Sobreescritura
        if self._estado_de_matricula.value in ("Retirado", "Anulado"):
            print(f"[Estudiante] Acceso denegado: {self.nombres} {self.apellidos} (matrícula {self._estado_de_matricula.value.lower()}).")
        else:
            print(f"[Estudiante] Sesión iniciada: {self.nombres} {self.apellidos} ({self._estado_de_matricula.value})")
    
    def formalizar_matricula(self): #Aspirante de la MTN en Estudiante
        pass
    
    def obtener_carrera(self):
        return self._carrera_registrada
    
    def obtener_registro_de_unidades_curriculares(self):
        pass
    
    def solicitar_retiro(self): #self, motivo
        pass