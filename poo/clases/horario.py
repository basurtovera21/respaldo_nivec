from __future__ import annotations

from datetime import time
from typing import Optional

from poo.clases.enums.dia_de_semana import DiaDeSemana

from poo.clases.interfaces.i_asignable_a_horario import IAsignableAHorario


class Horario:
    def __init__(self, dia_semana: DiaDeSemana, hora_inicio: time, hora_fin: time, espacio_de_imparticion: str = "", docente_responsable: Optional[IAsignableAHorario] = None, **kwargs):
        self.dia_semana = dia_semana
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.espacio_de_imparticion = espacio_de_imparticion
        self.docente_responsable = docente_responsable

    def obtener_resumen_de_sesion(self):
        return {
            "Día de semana": self.dia_semana.value,
            "Hora de inicio": str(self.hora_inicio),
            "Hora de finalización": str(self.hora_fin),
            "Duracion (en horas)": self.determinar_duracion_horas(),
            "Espacio de impartición": self.espacio_de_imparticion,
            "Docente responsable": f"{self.docente_responsable.nombres} {self.docente_responsable.apellidos}" if self.docente_responsable else "Sin asignar",
        }

    def determinar_duracion_horas(self):
        inicio = self.hora_inicio.hour + self.hora_inicio.minute / 60
        fin = self.hora_fin.hour + self.hora_fin.minute / 60
        return round(fin - inicio, 2)

    def verificar_conflicto_horario(self, otro_horario):
        if self.dia_semana != otro_horario.dia_semana:
            return False
        conflicto_horario = (self.hora_inicio < otro_horario.hora_fin) and (self.hora_fin > otro_horario.hora_inicio)
        return conflicto_horario

    def validar_datos_de_registro(self):
        errores = {}
        if self.hora_inicio is None or self.hora_fin is None:
            errores["hora_inicio"] = "Las horas de inicio y finalización son requeridas"
        elif self.hora_fin <= self.hora_inicio:
            errores["hora_fin"] = "La hora de finalización debe ser posterior a la hora de inicio"
        return errores
