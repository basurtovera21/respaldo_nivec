#Enums
from clases.enums.tipo_de_vinculacion import TipoDeVinculacion
from clases.enums.tiempo_de_dedicacion import TiempoDeDedicacion
from clases.enums.estado_de_vinculacion import EstadoDeVinculacion

#Herencia
from clases.usuarios.usuario_academico import UsuarioAcademico

#Interfaz
from clases.interfaces.i_asignable_a_horario import IAsignableAHorario

from clases.horario import Horario


class Docente(UsuarioAcademico, IAsignableAHorario):
    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, identificador_institucional: str, tipo_de_vinculacion: TipoDeVinculacion, tiempo_de_dedicacion: TiempoDeDedicacion, carga_horaria_maxima: float, **kwargs):
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
        self.tipo_de_vinculacion = tipo_de_vinculacion #Instancia
        self.tiempo_de_dedicacion = tiempo_de_dedicacion #Instancia
        self._estado_de_vinculacion = EstadoDeVinculacion.ACTIVO
        self.carga_horaria_maxima = carga_horaria_maxima #Límite normativo
        self._carga_horaria_actual = 0.0
        self._especialidades = [] #Áreas de conocimiento
        self._disponibilidad_semanal = [] #Bloque horario
        
        
    def iniciar_sesion(self): #Sobreescritura
        if self._estado_de_vinculacion.value == "Inactivo":
            return False
        return True
         
         
    def visualizar_carga_academica(self):
        horas_disponibles = self.carga_horaria_maxima - self._carga_horaria_actual
        if self._especialidades:
            especialidades = ", ".join(self._especialidades)
            
        else:
            especialidades = "No existen registros."
        
        return {
            "Docente": f"{self.nombres} {self.apellidos}",
            "Carga horaria actual": self._carga_horaria_actual,
            "Carga horaria máxima": self.carga_horaria_maxima,
            "Horas disponibles": horas_disponibles,
            "Especialidades": especialidades
        }
      
            
    def inhabilitar_perfil(self):
        self._estado_de_vinculacion = EstadoDeVinculacion.INACTIVO
        
        
    def verificar_disponibilidad_horaria(self, otro_horario: Horario):
        for horario_asignado in self._disponibilidad_semanal:
            if horario_asignado.verificar_conflicto_horario(otro_horario):
                return False
                
        return True