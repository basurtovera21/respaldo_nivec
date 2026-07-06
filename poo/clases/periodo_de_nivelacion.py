from datetime import date

# Enums
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo


class PeriodoDeNivelacion:
    def __init__(self, codigo_periodo: str, anio: int, periodo: str, fecha_inicio: date, fecha_fin: date, numero_periodo: int, estado: EstadoDePeriodo = EstadoDePeriodo.PLANIFICACION):
        self._codigo_periodo = codigo_periodo
        self._anio = anio
        self._periodo = periodo
        self._fecha_inicio = fecha_inicio
        self._fecha_fin = fecha_fin
        self._numero_periodo = numero_periodo
        self._estado = estado

    @property
    def codigo_periodo(self):
        return self._codigo_periodo

    @property
    def anio(self):
        return self._anio

    @property
    def periodo(self):
        return self._periodo

    @property
    def fecha_inicio(self):
        return self._fecha_inicio

    @property
    def fecha_fin(self):
        return self._fecha_fin

    @property
    def numero_periodo(self):
        return self._numero_periodo

    @property
    def estado(self):
        return self._estado

    def validar_datos_de_registro(self) -> dict:
        errores = {}
        if not self._anio:
            errores["anio"] = "Información requerida"
        if not self._numero_periodo:
            errores["numero_periodo"] = "Información requerida"
        elif self._numero_periodo not in (1, 2):
            errores["numero_periodo"] = "El registro no es válido (1 o 2)"
        if not self._fecha_inicio:
            errores["fecha_inicio"] = "Información requerida"
        if not self._fecha_fin:
            errores["fecha_fin"] = "Información requerida"
        return errores

    def validar_anio(self) -> str:
        anio_actual = date.today().year
        if self._anio and self._anio < anio_actual:
            return "El registro no es válido (año menor al actual)"
        return ""

    def validar_fechas(self) -> bool:
        if not self._fecha_inicio or not self._fecha_fin:
            return False
        return self._fecha_fin > self._fecha_inicio

    def iniciar_periodo_de_nivelacion(self) -> bool:
        if self._estado == EstadoDePeriodo.PLANIFICACION and date.today() >= self._fecha_inicio:
            self._estado = EstadoDePeriodo.EN_CURSO
            return True
        return False

    def finalizar_periodo_de_nivelacion(self) -> bool:
        if self._estado in (EstadoDePeriodo.EN_CURSO, EstadoDePeriodo.EVALUACION):
            self._estado = EstadoDePeriodo.CERRADO
            return True
        return False

    def calcular_duracion_semanas(self) -> int:
        if not self._fecha_inicio or not self._fecha_fin:
            return 0
        diferencia_tiempo = self._fecha_fin - self._fecha_inicio
        return diferencia_tiempo.days // 7

    def obtener_resumen_de_planificacion(self) -> dict:
        return {
            "Periodo": self._periodo,
            "Fecha de inicio": self._fecha_inicio,
            "Fecha de finalización": self._fecha_fin,
            "Duración (en semanas)": self.calcular_duracion_semanas(),
            "Estado": self._estado.value,
        }

    @staticmethod
    def validar_unico_en_curso(periodos_en_curso_count: int) -> bool:
        return periodos_en_curso_count == 0

    def validar_numero_de_semanas(self) -> str:
        semanas = getattr(self, '_numero_de_semanas', None) or self.calcular_duracion_semanas()
        if semanas < 6:
            return "El periodo debe tener un mínimo de 6 semanas"
        if semanas > 12:
            return "El periodo no puede exceder las 12 semanas"
        return ""

    # ── Consultas de estado (usadas por Django services.py) ──

    def esta_en_planificacion(self) -> bool:
        """Indica si el periodo está en estado de planificación."""
        return self._estado == EstadoDePeriodo.PLANIFICACION

    def esta_en_curso(self) -> bool:
        """Indica si el periodo está en curso."""
        return self._estado == EstadoDePeriodo.EN_CURSO

    def esta_en_evaluacion(self) -> bool:
        """Indica si el periodo está en fase de evaluación."""
        return self._estado == EstadoDePeriodo.EVALUACION

    def esta_cerrado(self) -> bool:
        """Indica si el periodo está cerrado/finalizado."""
        return self._estado == EstadoDePeriodo.CERRADO

    def permite_gestion_matriculas(self) -> bool:
        """
        Indica si el periodo permite gestionar matrículas manualmente.
        Solo en Planificación o En Curso.
        """
        return self._estado in (EstadoDePeriodo.PLANIFICACION, EstadoDePeriodo.EN_CURSO)

    def permite_configurar_horarios(self) -> bool:
        """Indica si se pueden crear/editar horarios (solo en Planificación)."""
        return self._estado == EstadoDePeriodo.PLANIFICACION

    def permite_evaluacion(self) -> bool:
        """Indica si se pueden gestionar calificaciones (solo en Evaluación)."""
        return self._estado == EstadoDePeriodo.EVALUACION
