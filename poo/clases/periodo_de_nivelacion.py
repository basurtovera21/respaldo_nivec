from datetime import date

# Enums
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo
from poo.clases.enums.modalidad import Modalidad


class PeriodoDeNivelacion:
    def __init__(self, codigo_periodo: str, anio: int, periodo: str, fecha_inicio: date, fecha_fin: date, modalidad: Modalidad, numero_periodo: int, estado: EstadoDePeriodo = EstadoDePeriodo.PLANIFICACION):
        self.codigo_periodo = codigo_periodo
        self.anio = anio
        self.periodo = periodo
        self.fecha_inicio = fecha_inicio  # datetime.date
        self.fecha_fin = fecha_fin        # datetime.date
        self.modalidad = modalidad        # Instancia
        self.numero_periodo = numero_periodo  # (1 o 2)
        self._estado = estado

    @property
    def estado(self):
        return self._estado

    def validar_fechas(self):
        return self.fecha_fin > self.fecha_inicio
            
    def iniciar_periodo_de_nivelacion(self):
        if self._estado == EstadoDePeriodo.PLANIFICACION and date.today() >= self.fecha_inicio:
            self._estado = EstadoDePeriodo.EN_CURSO
            return True
        return False
            
    def finalizar_periodo_de_nivelacion(self):
        if self._estado in (EstadoDePeriodo.EN_CURSO, EstadoDePeriodo.EVALUACION):
            self._estado = EstadoDePeriodo.CERRADO
            return True
        return False

    def calcular_duracion_semanas(self):
        diferencia_tiempo = self.fecha_fin - self.fecha_inicio
        return diferencia_tiempo.days // 7
    
    def obtener_resumen_de_planificacion(self):
        return {
            "Periodo": self.periodo,
            "Fecha de inicio": self.fecha_inicio,
            "Fecha de finalización": self.fecha_fin,
            "Modalidad": self.modalidad.value,
            "Duracion (en semanas)": self.calcular_duracion_semanas(),
            "Estado": self._estado.value,
        }

    def generar_matriz_de_horarios(self, paralelos: list):
        matriz_horarios = {}
        for paralelo in paralelos:
            matriz_horarios[paralelo.nombre] = paralelo.obtener_resumen_horario()
        return matriz_horarios