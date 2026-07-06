"""
Implementaciones concretas del patrón Chain of Responsibility para la
verificación de aprobación académica.

Cadena de prioridad normativa:
    1. ManejadorEstadoInactivo: Estado RETIRADO/ANULADO es definitivo
    2. ManejadorAsistencia: Asistencia insuficiente → REPROBADO
    3. ManejadorCalificacion: Nota final vs criterio → APROBADO/REPROBADO

Principios:
    - SRP: Cada manejador valida un único criterio
    - OCP: Se pueden agregar nuevos manejadores sin modificar los existentes
    - LSP: Todos los manejadores son intercambiables (misma interfaz)
"""

from poo.clases.interfaces.i_manejador_de_aprobacion import IManejadorDeAprobacion
from poo.clases.enums.estado_de_aprobacion import EstadoDeAprobacion


class ManejadorEstadoInactivo(IManejadorDeAprobacion):
    """
    Primer eslabón: Verifica si el estudiante tiene un estado definitivo
    (RETIRADO o ANULADO). Si es así, termina la cadena.
    """

    def manejar(self, evaluacion_academica):
        if evaluacion_academica._estado_de_aprobacion in (
            EstadoDeAprobacion.RETIRADO, EstadoDeAprobacion.ANULADO
        ):
            return evaluacion_academica._estado_de_aprobacion

        if self.siguiente:
            return self.siguiente.manejar(evaluacion_academica)
        return evaluacion_academica._estado_de_aprobacion


class ManejadorAsistencia(IManejadorDeAprobacion):
    """
    Segundo eslabón: Verifica que el porcentaje de asistencia cumpla
    el mínimo requerido por la unidad curricular.
    Si no cumple → REPROBADO por asistencia insuficiente.
    """

    def manejar(self, evaluacion_academica):
        porcentaje_minimo = evaluacion_academica.unidad_curricular.porcentaje_minimo_asistencia

        if evaluacion_academica._porcentaje_asistencia < porcentaje_minimo:
            evaluacion_academica._estado_de_aprobacion = EstadoDeAprobacion.REPROBADO
            evaluacion_academica._observacion = "Reprobado por porcentaje de asistencia insuficiente"
            return evaluacion_academica._estado_de_aprobacion

        if self.siguiente:
            return self.siguiente.manejar(evaluacion_academica)
        return evaluacion_academica._estado_de_aprobacion


class ManejadorCalificacion(IManejadorDeAprobacion):
    """
    Tercer eslabón: Compara la nota final con el criterio de aprobación
    de la unidad curricular.
    Si nota >= criterio → APROBADO
    Si nota < criterio → REPROBADO por calificación insuficiente
    """

    def manejar(self, evaluacion_academica):
        criterio = evaluacion_academica.unidad_curricular.criterio_de_aprobacion

        if evaluacion_academica._nota_final >= criterio:
            evaluacion_academica._estado_de_aprobacion = EstadoDeAprobacion.APROBADO
            evaluacion_academica._observacion = "Aprobado"
        else:
            evaluacion_academica._estado_de_aprobacion = EstadoDeAprobacion.REPROBADO
            evaluacion_academica._observacion = "Reprobado por calificación insuficiente"

        if self.siguiente:
            return self.siguiente.manejar(evaluacion_academica)
        return evaluacion_academica._estado_de_aprobacion
