# Enum
from poo.clases.enums.estado_de_aprobacion import EstadoDeAprobacion

# Usuario
from poo.clases.usuarios.estudiante import Estudiante

# Unidad Curricular
from poo.clases.unidad_curricular import UnidadCurricular

# Interfaces y Servicios (Patrones de Diseño)
from poo.clases.interfaces.i_sujeto_de_evaluacion import ISujetoDeEvaluacion
from poo.clases.servicios.manejadores_de_aprobacion import ManejadorEstadoInactivo, ManejadorAsistencia, ManejadorCalificacion


class EvaluacionAcademica(ISujetoDeEvaluacion):
    """
    Entidad que gestiona la evaluación académica de un estudiante en una unidad curricular.

    Patrones de diseño implementados:
        - Chain of Responsibility: La verificación de aprobación se delega a una cadena
          de manejadores (EstadoInactivo → Asistencia → Calificación) que procesan
          la evaluación en orden de prioridad normativa.
        - Observer (ISujetoDeEvaluacion): Al cambiar el estado de aprobación, se notifica
          automáticamente a los observadores suscritos (ej: ObservadorEstadoEstudiante,
          ObservadorInformeGeneral).

    Principios:
        - SRP: Gestiona solo la lógica de evaluación académica
        - OCP: Nuevas reglas de aprobación se agregan como manejadores sin modificar esta clase
        - Encapsulación: Estado interno protegido, acceso controlado vía properties

    Sobrecarga:
        - registrar_calificacion(*args): Acepta (parcial, nota) o (nota1, nota2)
    """

    # ── Constantes de negocio ──
    NOTA_MINIMA = 0.0
    NOTA_MAXIMA = 10.0
    PORCENTAJE_ASISTENCIA_MINIMO = 0.0
    PORCENTAJE_ASISTENCIA_MAXIMO = 100.0

    def __init__(self, estudiante: Estudiante, unidad_curricular: UnidadCurricular):
        super().__init__()  # Inicializar la lista de observadores del sujeto (Observer)
        self._estudiante = estudiante
        self._unidad_curricular = unidad_curricular
        self._calificacion_parcial_1 = 0.0
        self._calificacion_parcial_2 = 0.0
        self._nota_final = 0.0
        self._porcentaje_asistencia = 0.0
        self._estado_de_aprobacion = EstadoDeAprobacion.PENDIENTE
        self._observacion = ""
        # Patrón Chain of Responsibility
        self._cadena_aprobacion = ManejadorEstadoInactivo(
            ManejadorAsistencia(ManejadorCalificacion())
        )

    # ── Properties (Encapsulación) ──

    @property
    def estudiante(self):
        return self._estudiante

    @property
    def unidad_curricular(self):
        return self._unidad_curricular

    @property
    def calificacion_parcial_1(self):
        return self._calificacion_parcial_1

    @property
    def calificacion_parcial_2(self):
        return self._calificacion_parcial_2

    @property
    def nota_final(self):
        return self._nota_final

    @property
    def porcentaje_asistencia(self):
        return self._porcentaje_asistencia

    @property
    def estado_de_aprobacion(self):
        return self._estado_de_aprobacion

    @property
    def observacion(self):
        return self._observacion

    # ── Registro de calificaciones (Sobrecarga) ──

    def registrar_calificacion(self, *args):
        """
        Registra calificaciones parciales. Soporta dos formas de invocación (sobrecarga):

        1. registrar_calificacion(parcial: int, nota: float)
           → Registra la nota en el parcial especificado (1 o 2)

        2. registrar_calificacion(nota1: float, nota2: float)
           → Registra ambos parciales simultáneamente

        No permite modificar calificaciones si el estado ya no es PENDIENTE.

        Returns:
            True si el registro fue exitoso, False si falló la validación
        """
        if self._estado_de_aprobacion != EstadoDeAprobacion.PENDIENTE:
            return False

        # Para parcial específico: (parcial: int, nota: float)
        if len(args) == 2 and isinstance(args[0], int):
            parcial, nota = args
            return self._definir_en_parcial(parcial, nota)

        # Para ambos parciales: (nota1: float, nota2: float)
        elif len(args) == 2 and isinstance(args[0], float):
            resultado_p1 = self._definir_en_parcial(1, args[0])
            resultado_p2 = self._definir_en_parcial(2, args[1])
            return resultado_p1 and resultado_p2

        return False

    def _definir_en_parcial(self, parcial: int, nota: float) -> bool:
        """
        Valida el rango de la nota y la asigna al parcial indicado.

        Args:
            parcial: Número de parcial (1 o 2)
            nota: Calificación a registrar (0.0 - 10.0)

        Returns:
            True si se registró correctamente
        """
        if not (self.NOTA_MINIMA <= nota <= self.NOTA_MAXIMA):
            return False

        if parcial == 1:
            self._calificacion_parcial_1 = nota
            return True
        elif parcial == 2:
            self._calificacion_parcial_2 = nota
            return True

        return False

    # ── Cálculos académicos ──

    def calcular_nota_final(self) -> float:
        """
        Calcula la nota final como promedio de los dos parciales.
        Solo calcula si ambos parciales tienen valor distinto de cero.

        Returns:
            La nota final calculada (0.0 si algún parcial no ha sido registrado)
        """
        if self._calificacion_parcial_1 == 0.0 or self._calificacion_parcial_2 == 0.0:
            return 0.0

        self._nota_final = round(
            (self._calificacion_parcial_1 + self._calificacion_parcial_2) / 2, 2
        )
        return self._nota_final

    def registrar_asistencia_final(self, porcentaje: float) -> bool:
        """
        Registra el porcentaje de asistencia final del estudiante.

        Args:
            porcentaje: Valor entre 0.0 y 100.0

        Returns:
            True si el registro fue exitoso, False si el valor está fuera de rango
        """
        if not (self.PORCENTAJE_ASISTENCIA_MINIMO <= porcentaje <= self.PORCENTAJE_ASISTENCIA_MAXIMO):
            return False

        self._porcentaje_asistencia = porcentaje
        return True

    # ── Verificación de aprobación (Chain of Responsibility + Observer) ──

    def verificar_aprobacion(self) -> EstadoDeAprobacion:
        """
        Determina el estado final de aprobación delegando a la cadena de manejadores.

        Flujo de la cadena (Chain of Responsibility):
            1. ManejadorEstadoInactivo: Si está RETIRADO/ANULADO → termina
            2. ManejadorAsistencia: Si asistencia < mínimo → REPROBADO
            3. ManejadorCalificacion: Si nota >= criterio → APROBADO, sino → REPROBADO

        Si el estado cambia de PENDIENTE a otro, se notifica a los observadores (Observer).

        Returns:
            EstadoDeAprobacion resultante
        """
        estado_anterior = self._estado_de_aprobacion

        # Chain of Responsibility
        self._cadena_aprobacion.manejar(self)

        # Si el estado cambió (dejó de estar PENDIENTE), notificación al Observer
        if (estado_anterior == EstadoDeAprobacion.PENDIENTE
                and self._estado_de_aprobacion != EstadoDeAprobacion.PENDIENTE):
            self.notificar()

        return self._estado_de_aprobacion

    # ── Comportamiento de dominio ──

    def obtener_resumen_de_evaluacion(self) -> dict:
        """
        Retorna un resumen estructurado de la evaluación académica.
        Útil para reportes, informes y actas de paralelo.
        """
        return {
            "Estudiante": f"{self._estudiante.nombres} {self._estudiante.apellidos}",
            "Unidad_curricular": self._unidad_curricular.nombre,
            "Calificación parcial 1": self._calificacion_parcial_1,
            "Calificación parcial 2": self._calificacion_parcial_2,
            "Nota final": self._nota_final,
            "Porcentaje de asistencia": self._porcentaje_asistencia,
            "Estado de aprobación": self._estado_de_aprobacion.value,
            "Observación": self._observacion,
        }

    def esta_aprobado(self) -> bool:
        """Indica si el estudiante aprobó la unidad curricular."""
        return self._estado_de_aprobacion == EstadoDeAprobacion.APROBADO

    def esta_finalizada(self) -> bool:
        """Indica si la evaluación ya fue procesada (no está pendiente)."""
        return self._estado_de_aprobacion != EstadoDeAprobacion.PENDIENTE

    # ── Método de clase ──

    @classmethod
    def registrar_evaluacion_de_paralelo(cls, evaluaciones_academicas: list) -> list:
        """
        Genera el acta de evaluación de un paralelo completo.

        Args:
            evaluaciones_academicas: Lista de instancias de EvaluacionAcademica

        Returns:
            Lista de resúmenes (diccionarios) de cada evaluación
        """
        evaluacion_de_paralelo = []

        for evaluacion_academica in evaluaciones_academicas:
            resumen_de_estudiante = evaluacion_academica.obtener_resumen_de_evaluacion()
            evaluacion_de_paralelo.append(resumen_de_estudiante)

        return evaluacion_de_paralelo
