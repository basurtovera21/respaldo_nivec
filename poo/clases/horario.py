from datetime import time

#Enums
from poo.clases.enums.dia_de_semana import DiaDeSemana
from poo.clases.enums.modalidad import Modalidad
from poo.clases.enums.tipo_de_sesion import TipoDeSesion

#Interfaz
from poo.clases.interfaces.i_asignable_a_horario import IAsignableAHorario


class Horario:
    def __init__(self, dia_semana: DiaDeSemana, hora_inicio: time, hora_fin: time, espacio_de_imparticion: str, modalidad: Modalidad, numero_semana: int, tipo_de_sesion: TipoDeSesion, docente_responsable: IAsignableAHorario | None = None):
        self.dia_semana = dia_semana #Instancia
        self.hora_inicio = hora_inicio #datetime.time
        self.hora_fin = hora_fin #datetime.time
        self.espacio_de_imparticion = espacio_de_imparticion
        self.modalidad = modalidad # Instancia
        self.numero_semana = numero_semana
        self.tipo_de_sesion = tipo_de_sesion #Instancia
        self.docente_responsable = docente_responsable #Instancia Docente
        

    def obtener_resumen_de_sesion(self):
        return {
            "Día de semana": self.dia_semana.value,
            "Hora de inicio": str(self.hora_inicio),
            "Hora de finalización": str(self.hora_fin),
            "Duracion (en horas)": self.determinar_duracion_horas(),
            "Espacio de impartición": self.espacio_de_imparticion,
            "Modalidad": self.modalidad.value,
            "Tipo de sesión": self.tipo_de_sesion.value,
            "Docente responsable": f"{self.docente_responsable.nombres} {self.docente_responsable.apellidos}" if self.docente_responsable else "Sin asignar",
        }
        
        
    def determinar_duracion_horas(self): #Retorna float
      inicio = self.hora_inicio.hour + self.hora_inicio.minute/60
      fin = self.hora_fin.hour + self.hora_fin.minute/60
      return round(fin - inicio, 2) 
  
  
    def verificar_conflicto_horario(self, otro_horario):
        if self.dia_semana != otro_horario.dia_semana:
            return False
    
        if self.numero_semana != otro_horario.numero_semana:
            return False

        conflicto_horario = (self.hora_inicio < otro_horario.hora_fin) and (self.hora_fin > otro_horario.hora_inicio)
        return conflicto_horario
    
    def validar_datos_de_registro(self):
        errores = {}

        if self.hora_inicio is None or self.hora_fin is None:
            errores["hora_inicio"] = "Las horas de inicio y finalización son requeridas"
        elif self.hora_fin <= self.hora_inicio:
            errores["hora_fin"] = "La hora de finalización debe ser posterior a la hora de inicio"

        if not isinstance(self.numero_semana, int) or self.numero_semana <= 0:
            errores["numero_semana"] = "El número de semana debe ser un entero mayor a cero"

        if not self.espacio_de_imparticion or not str(self.espacio_de_imparticion).strip():
            errores["espacio_de_imparticion"] = "El espacio de impartición es requerido"

        return errores
