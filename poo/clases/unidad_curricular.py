# Interfaz
from poo.clases.interfaces.i_unidad_evaluable import IUnidadEvaluable


class UnidadCurricular(IUnidadEvaluable):
    """
    Entidad que representa una asignatura o materia dentro de una malla curricular.

    Responsabilidades:
        - Encapsular los datos académicos de una unidad curricular
        - Validar la distribución coherente de horas (sincrónicas + asincrónicas = totales)
        - Validar criterios de aprobación y asistencia dentro de rangos normativos
        - Proveer información estructurada para reportes

    Principios:
        - SRP: Solo gestiona datos y reglas de negocio de la unidad curricular
        - ISP: Implementa IUnidadEvaluable (solo los métodos que la malla necesita)
        - OCP: Usa CriterioConsistenteDeHoras (Strategy) para validación de horas,
          permitiendo cambiar la regla sin modificar esta clase

    Interfaces implementadas:
        - IUnidadEvaluable: obtener_codigo_de_unidad(), obtener_horas_totales()
    """

    # ── Constantes de negocio ──
    MINIMO_HORAS_SINCRONICAS = 6
    CRITERIO_APROBACION_MINIMO = 0.0
    CRITERIO_APROBACION_MAXIMO = 10.0
    PORCENTAJE_ASISTENCIA_MINIMO = 0.0
    PORCENTAJE_ASISTENCIA_MAXIMO = 100.0

    def __init__(self, codigo_de_unidad: str, nombre: str, horas_totales: float,
                 horas_sincronicas: float, horas_asincronicas: float,
                 criterio_de_aprobacion: float = 7.0,
                 porcentaje_minimo_asistencia: float = 70.0, **kwargs):
        self._codigo_de_unidad = codigo_de_unidad
        self._nombre = nombre
        self._horas_totales = horas_totales
        self._horas_sincronicas = horas_sincronicas
        self._horas_asincronicas = horas_asincronicas
        self._criterio_de_aprobacion = criterio_de_aprobacion
        self._porcentaje_minimo_asistencia = porcentaje_minimo_asistencia

    # ── Properties (Encapsulación) ──

    @property
    def codigo_de_unidad(self):
        return self._codigo_de_unidad

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        self._nombre = valor

    @property
    def horas_totales(self):
        return self._horas_totales

    @property
    def horas_sincronicas(self):
        return self._horas_sincronicas

    @property
    def horas_asincronicas(self):
        return self._horas_asincronicas

    @property
    def criterio_de_aprobacion(self):
        return self._criterio_de_aprobacion

    @property
    def porcentaje_minimo_asistencia(self):
        return self._porcentaje_minimo_asistencia

    # ── Implementación de IUnidadEvaluable ──

    def obtener_codigo_de_unidad(self):
        """Retorna el código único de la unidad curricular (requerido por IUnidadEvaluable)."""
        return self._codigo_de_unidad

    def obtener_horas_totales(self):
        """Retorna el total de horas de la unidad curricular (requerido por IUnidadEvaluable)."""
        return self._horas_totales

    # ── Validaciones de negocio ──

    def validar_distribucion_de_horas_totales(self) -> bool:
        """
        Verifica que la suma de horas sincrónicas y asincrónicas sea igual
        al total de horas registrado. Delega al criterio Strategy.

        Returns:
            True si la distribución es consistente
        """
        from poo.clases.criterios_filtro.criterio_consistente_de_horas import CriterioConsistenteDeHoras

        criterio = CriterioConsistenteDeHoras()
        return criterio.es_valido({
            "horas_totales": self._horas_totales,
            "horas_sincronicas": self._horas_sincronicas,
            "horas_asincronicas": self._horas_asincronicas,
        })

    def validar_horas(self) -> dict:
        """
        Valida que las horas sean coherentes:
        - Horas totales mayor a cero
        - Horas sincrónicas y asincrónicas no negativas
        - Distribución consistente (sincrónicas + asincrónicas = totales)

        Returns:
            dict con errores por campo (vacío si todo es correcto)
        """
        errores = {}

        if self._horas_totales <= 0:
            errores["horas_totales"] = "El registro debe ser mayor a cero"

        if self._horas_sincronicas < 0:
            errores["horas_sincronicas"] = "El registro no puede ser negativo"

        if self._horas_asincronicas < 0:
            errores["horas_asincronicas"] = "El registro no puede ser negativo"

        if not self.validar_distribucion_de_horas_totales():
            errores["horas_totales"] = (
                "El total de horas sincrónicas y horas asincrónicas "
                "no coincide con el total registrado"
            )

        return errores

    def validar_criterios(self) -> dict:
        """
        Valida que los criterios de aprobación y asistencia estén dentro
        de los rangos normativos establecidos.

        Returns:
            dict con errores por campo (vacío si todo es correcto)
        """
        errores = {}

        if not (self.CRITERIO_APROBACION_MINIMO <= self._criterio_de_aprobacion <= self.CRITERIO_APROBACION_MAXIMO):
            errores["criterio_de_aprobacion"] = (
                f"El registro debe estar entre "
                f"{self.CRITERIO_APROBACION_MINIMO} y {self.CRITERIO_APROBACION_MAXIMO}"
            )

        if not (self.PORCENTAJE_ASISTENCIA_MINIMO <= self._porcentaje_minimo_asistencia <= self.PORCENTAJE_ASISTENCIA_MAXIMO):
            errores["porcentaje_minimo_asistencia"] = (
                f"El registro debe estar entre "
                f"{self.PORCENTAJE_ASISTENCIA_MINIMO} y {self.PORCENTAJE_ASISTENCIA_MAXIMO}"
            )

        return errores

    def validar_datos_de_registro(self) -> dict:
        """
        Validación completa para el registro de una unidad curricular.
        Incluye: nombre obligatorio, mínimo de horas sincrónicas,
        distribución de horas y criterios normativos.

        Returns:
            dict con errores por campo (vacío si todo es correcto)
        """
        errores = {}

        if not self._nombre or not self._nombre.strip():
            errores["nombre"] = "Información requerida"

        if self._horas_sincronicas is not None and self._horas_sincronicas < self.MINIMO_HORAS_SINCRONICAS:
            errores["horas_sincronicas"] = (
                f"Las horas sincrónicas deben ser al menos {self.MINIMO_HORAS_SINCRONICAS}"
            )

        errores.update(self.validar_horas())
        errores.update(self.validar_criterios())

        return errores

    # ── Comportamiento de dominio ──

    def recuperar_informacion_de_unidad(self) -> dict:
        """
        Retorna un resumen estructurado de los datos de la unidad curricular.
        Útil para reportes, informes y visualización.
        """
        return {
            "Código de unidad": self._codigo_de_unidad,
            "Unidad curricular": self._nombre,
            "Horas totales": self._horas_totales,
            "Horas sincrónicas": self._horas_sincronicas,
            "Horas asincrónicas": self._horas_asincronicas,
            "Criterio de aprobación": self._criterio_de_aprobacion,
            "Porcentaje mínimo de asistencia": self._porcentaje_minimo_asistencia,
            "Distribución válida": self.validar_distribucion_de_horas_totales(),
        }

    def __str__(self):
        return f"{self._codigo_de_unidad} ({self._nombre})"
