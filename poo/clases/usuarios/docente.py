from poo.clases.usuarios.usuario_academico import UsuarioAcademico
from poo.clases.interfaces.i_asignable_a_horario import IAsignableAHorario
from poo.clases.enums.estado_de_vinculacion import EstadoDeVinculacion
from poo.clases.horario import Horario

class Docente(UsuarioAcademico, IAsignableAHorario):
    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, 
                 correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, 
                 etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, 
                 identificador_institucional: str, universidad, tipo_de_vinculacion, 
                 tiempo_de_dedicacion, carga_horaria_maxima: float, 
                 estado_vinculacion=EstadoDeVinculacion.ACTIVO, **kwargs):
        
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
            identificador_institucional=identificador_institucional,
            **kwargs
        )
        
        self._universidad = universidad
        self._tipo_de_vinculacion = tipo_de_vinculacion
        self._tiempo_de_dedicacion = tiempo_de_dedicacion
        self._carga_horaria_maxima = carga_horaria_maxima
        
        self._estado_de_vinculacion = estado_vinculacion
        self._carga_horaria_actual = 0.0
        self._disponibilidad_semanal = []
        
    @property
    def nombres(self):
        return self._nombres

    @nombres.setter
    def nombres(self, value):
        self._nombres = value

    @property
    def apellidos(self):
        return self._apellidos

    @apellidos.setter
    def apellidos(self, value):
        self._apellidos = value

    @property
    def universidad(self):
        return self._universidad
        
    @property
    def tipo_de_vinculacion(self):
        return self._tipo_de_vinculacion

    @property
    def tiempo_de_dedicacion(self):
        return self._tiempo_de_dedicacion

    @property
    def carga_horaria_maxima(self):
        return self._carga_horaria_maxima

    @property
    def estado_de_vinculacion(self):
        return self._estado_de_vinculacion

    def iniciar_sesion(self):
        if self._estado_de_vinculacion.value == "Inactivo":
            return False
        return True

    def visualizar_carga_academica(self):
        horas_disponibles = self.carga_horaria_maxima - self._carga_horaria_actual
        
        return {
            "Docente": f"{self.nombres} {self.apellidos}",
            "Universidad": str(self.universidad),
            "Carga horaria actual": self._carga_horaria_actual,
            "Carga horaria máxima": self.carga_horaria_maxima,
            "Horas disponibles": horas_disponibles,
        }

    def inhabilitar(self):
        self._estado_de_vinculacion = EstadoDeVinculacion.INACTIVO
        
    def habilitar(self):
        self._estado_de_vinculacion = EstadoDeVinculacion.ACTIVO

    def verificar_disponibilidad_horaria(self, otro_horario: Horario):
        for horario_asignado in self._disponibilidad_semanal:
            if horario_asignado.verificar_conflicto_horario(otro_horario):
                return False
        return True

    def establecer_estado_de_vinculacion(self, estado: EstadoDeVinculacion):
        self._estado_de_vinculacion = estado

    def registrar_carga_actual(self, horas: float):
        self._carga_horaria_actual = round(float(horas or 0), 2)

    def agregar_horario_ocupado(self, horario: Horario):
        self._disponibilidad_semanal.append(horario)

    def esta_activo(self):
        return self._estado_de_vinculacion == EstadoDeVinculacion.ACTIVO

    def validar_asignacion_a_paralelo(self, paralelo, horas_de_la_unidad):
        if not self.esta_activo():
            return {"ok": False, "motivo": "inactivo"}

        for horario in paralelo.horarios:
            if not self.verificar_disponibilidad_horaria(horario):
                return {"ok": False, "motivo": "conflicto", "horario_en_conflicto": horario}

        horas_nuevas = round(float(horas_de_la_unidad or 0), 2)
        if self._carga_horaria_actual + horas_nuevas > self.carga_horaria_maxima:
            return {
                "ok": False,
                "motivo": "carga",
                "carga_actual": self._carga_horaria_actual,
                "horas_nuevas": horas_nuevas,
                "carga_maxima": self.carga_horaria_maxima,
            }

        return {"ok": True, "motivo": ""}