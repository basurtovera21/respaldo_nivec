#Enums
from poo.clases.enums.jornada import Jornada
from poo.clases.enums.modalidad import Modalidad

#Usuarios
from poo.clases.usuarios.docente import Docente
from poo.clases.usuarios.estudiante import Estudiante

from poo.clases.horario import Horario


class Paralelo:
    CAPACIDAD_MAXIMA_PREDETERMINADA = 35

    def __init__(self, codigo_de_paralelo: str, nombre: str, jornada: Jornada, modalidad: Modalidad, capacidad_maxima: int = None):
        self.codigo_de_paralelo = codigo_de_paralelo
        self.nombre = nombre
        self.jornada = jornada
        self.modalidad = modalidad
        self.capacidad_maxima = capacidad_maxima if capacidad_maxima is not None else Paralelo.CAPACIDAD_MAXIMA_PREDETERMINADA
        self._docente_responsable = None
        self._estudiantes_matriculados = []
        self.horarios = []


    def validar_datos_de_registro(self):
        errores = {}

        if not self.nombre or not self.nombre.strip():
            errores["nombre"] = "Información requerida"

        if not isinstance(self.jornada, Jornada):
            errores["jornada"] = "Jornada no válida"

        if not isinstance(self.modalidad, Modalidad):
            errores["modalidad"] = "Modalidad no válida"

        if not isinstance(self.capacidad_maxima, int) or self.capacidad_maxima <= 0:
            errores["capacidad_maxima"] = "La capacidad máxima debe ser un número entero mayor a cero"

        return errores


    def tiene_cupo_disponible(self):
        return len(self._estudiantes_matriculados) < self.capacidad_maxima


    def vincular_estudiante(self, estudiante: Estudiante):
        if not self.tiene_cupo_disponible():
            return False

        if estudiante in self._estudiantes_matriculados:
            return False

        self._estudiantes_matriculados.append(estudiante)
        return True


    def desvincular_estudiante(self, estudiante: Estudiante):
        if estudiante not in self._estudiantes_matriculados:
            return False

        self._estudiantes_matriculados.remove(estudiante)
        return True


    def vincular_docente(self, docente: Docente):
        if self._docente_responsable is not None:
            return False

        self._docente_responsable = docente
        return True


    def desvincular_docente(self):
        if self._docente_responsable is None:
            return False

        self._docente_responsable = None
        return True


    def agregar_horario(self, horario: Horario):
        self.horarios.append(horario)
        
    def calcular_horas_agendadas(self):
        total_de_horas = 0.0
        for horario in self.horarios:
            total_de_horas += horario.determinar_duracion_horas()
        return round(total_de_horas, 2)

    def encontrar_conflicto_horario(self, nuevo_horario, horarios_externos=None):
        horarios_a_revisar = list(self.horarios)
        if horarios_externos:
            horarios_a_revisar.extend(horarios_externos)

        for horario in horarios_a_revisar:
            if nuevo_horario.verificar_conflicto_horario(horario):
                return horario
        return None

    def validar_nuevo_horario(self, nuevo_horario, horas_sincronicas_requeridas, horarios_externos=None):
        conflicto = self.encontrar_conflicto_horario(nuevo_horario, horarios_externos)
        if conflicto is not None:
            return {"ok": False, "motivo": "conflicto", "horario_en_conflicto": conflicto}

        horas_actuales = self.calcular_horas_agendadas()
        horas_nuevas = nuevo_horario.determinar_duracion_horas()
        if horas_actuales + horas_nuevas > horas_sincronicas_requeridas:
            return {
                "ok": False,
                "motivo": "horas",
                "horas_actuales": horas_actuales,
                "horas_nuevas": horas_nuevas,
            }

        return {"ok": True, "motivo": ""}
 
 
    def obtener_resumen_horario(self):
        lista_de_resumenes_horarios = []

        for horario in self.horarios:
            resumen_de_la_sesion = horario.obtener_resumen_de_sesion()
            lista_de_resumenes_horarios.append(resumen_de_la_sesion)

        return lista_de_resumenes_horarios


    def obtener_resumen(self):
        return {
            "Código de paralelo": self.codigo_de_paralelo,
            "Nombre": self.nombre,
            "Jornada": self.jornada.value,
            "Modalidad": self.modalidad.value,
            "Capacidad máxima": self.capacidad_maxima,
            "Estudiantes matriculados": len(self._estudiantes_matriculados),
            "Cupos disponibles": self.capacidad_maxima - len(self._estudiantes_matriculados),
            "Docente responsable": (
                f"{self._docente_responsable.nombres} {self._docente_responsable.apellidos}"
                if self._docente_responsable else "Sin asignar"
            ),
        }