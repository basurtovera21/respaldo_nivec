from datetime import time
from clases.enums.dia_de_semana import DiaDeSemana
from clases.enums.modalidad import Modalidad
from clases.enums.tipo_de_sesion import TipoDeSesion

#Usuario
from clases.usuarios.docente import Docente

class Horario:
    def __init__(self, dia_semana: DiaDeSemana, hora_inicio: time, hora_fin: time, espacio_de_imparticion: str, modalidad: Modalidad, numero_semana: int, tipo_de_sesion: TipoDeSesion, docente_responsable: Docente):
        self.dia_semana = dia_semana #Instancia
        self.hora_inicio = hora_inicio #Instancia datetime.time
        self.hora_fin = hora_fin #Instancia datetime.time
        self.espacio_de_imparticion = espacio_de_imparticion
        self.modalidad = modalidad # Instancia
        self.numero_semana = numero_semana
        self.tipo_de_sesion = tipo_de_sesion #Instancia
        self.docente_responsable = docente_responsable #Instancia Docente
        

    def obtener_resumen_de_sesion(self): #Retorna dict
        pass
    def determinar_duracion_horas(self): #Retorna float
      inicio = self.hora_inicio.hour + self.hora_inicio.minute/60
      fin = self.hora_fin.hour + self.hora_fin.minute/60
      return round(fin - inicio, 2) 
  
    def verificar_conflicto_horario(self, otro_horario: 'Horario'):
        if self.dia_semana != otro_horario.dia_semana:
            return False
    
        if self.numero_semana != otro_horario.numero_semana:
            return False

        conflicto_horario = (self.hora_inicio < otro_horario.hora_fin) and (self.hora_fin > otro_horario.hora_inicio)
        return conflicto_horario