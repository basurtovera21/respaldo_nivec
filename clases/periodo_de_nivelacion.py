from datetime import date

#Enums
from clases.enums.estado_de_periodo import EstadoDePeriodo
from clases.enums.modalidad import Modalidad


class PeriodoDeNivelacion:
    def __init__(self, codigo_periodo: str, anio: int, periodo: str, fecha_inicio: date, fecha_fin: date, modalidad: Modalidad, numero_periodo: int):
        self.codigo_periodo = codigo_periodo
        self.anio = anio
        self.periodo = periodo
        self.fecha_inicio = fecha_inicio #datetime.date
        self.fecha_fin = fecha_fin # datetime.date
        self.modalidad = modalidad # Instancia
        self.numero_periodo = numero_periodo #(1 o 2)
        self._estado = EstadoDePeriodo.PLANIFICACION
        

    def iniciar_periodo_de_nivelacion(self):
        #PLANIFICACION a EN_CURSO
        puede_iniciar = (self._estado == EstadoDePeriodo.PLANIFICACION and date.today() >= self.fecha_inicio)
        if puede_iniciar:
            self._estado = EstadoDePeriodo.EN_CURSO
            return True
        
        return False
            
            
    def finalizar_periodo_de_nivelacion(self):
        #Estado a CERRADO
        puede_finalizar = self._estado in (EstadoDePeriodo.EN_CURSO, EstadoDePeriodo.EVALUACION)
        if puede_finalizar:
            self._estado = EstadoDePeriodo.CERRADO
            return True
        
        return False


    def calcular_duracion_semanas(self):
        diferencia_tiempo = self.fecha_fin - self.fecha_inicio
        total_días = diferencia_tiempo.days
        semanas_totales = total_días//7
        return semanas_totales
    
    
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
        #Resumen de todos los horarios del periodo.

        matriz_horarios = {}
        for paralelo in paralelos:
            resumen_del_paralelo = paralelo.obtener_resumen_horario()
            matriz_horarios[paralelo.nombre] = resumen_del_paralelo #Guardar el resumen en la matriz usando el nombre del paralelo

        return matriz_horarios