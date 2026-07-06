"""
Implementaciones concretas del patrón Observer para la evaluación académica.

Estos observadores se suscriben a una EvaluacionAcademica (ISujetoDeEvaluacion)
y son notificados automáticamente cuando el estado de aprobación cambia.

Uso:
    evaluacion = EvaluacionAcademica(estudiante, unidad)
    evaluacion.anexar(ObservadorEstadoEstudiante())
    evaluacion.anexar(ObservadorInformeGeneral())
    # Al llamar verificar_aprobacion(), si el estado cambia, se notifica a ambos
"""

from poo.clases.interfaces.i_observador_de_evaluacion import IObservadorDeEvaluacion
from poo.clases.enums.estado_de_aprobacion import EstadoDeAprobacion


class ObservadorEstadoEstudiante(IObservadorDeEvaluacion):
    """
    Observador que reacciona al cambio de estado de aprobación del estudiante.
    En producción puede disparar notificaciones, actualizar dashboards, etc.
    """

    def actualizar(self, evaluacion_academica):
        estudiante = evaluacion_academica.estudiante
        estado_final = evaluacion_academica._estado_de_aprobacion

        print(
            f"[Observer] Estudiante: {estudiante.nombres} {estudiante.apellidos} "
            f"({estudiante.identificacion}). "
            f"Estado en {evaluacion_academica.unidad_curricular.nombre}: {estado_final.value}"
        )


class ObservadorInformeGeneral(IObservadorDeEvaluacion):
    """
    Observador que registra datos de rendimiento para el procesamiento
    de informes institucionales cuando una evaluación se cierra.
    """

    def actualizar(self, evaluacion_academica):
        if evaluacion_academica._estado_de_aprobacion != EstadoDeAprobacion.PENDIENTE:
            resumen = evaluacion_academica.obtener_resumen_de_evaluacion()
            print(
                f"[Observer/Informe] Estudiante: {resumen['Estudiante']}. "
                f"Nota Final: {resumen['Nota final']}. "
                f"Estado: {resumen['Estado de aprobación']}"
            )
