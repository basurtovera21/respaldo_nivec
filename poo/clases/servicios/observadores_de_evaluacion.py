from clases.interfaces.i_observador_de_evaluacion import IObservadorDeEvaluacion
from clases.enums.estado_de_aprobacion import EstadoDeAprobacion
from clases.evaluacion_academica import EvaluacionAcademica

class ObservadorEstadoEstudiante(IObservadorDeEvaluacion):
    def actualizar(self, evaluacion_academica: EvaluacionAcademica):
    #Reacciona al cambio de estado de la evaluación académica del estudiante.
        estudiante = evaluacion_academica.estudiante
        estado_final = evaluacion_academica._estado_de_aprobacion
        
        print(f"(Estudiante): {estudiante.nombres} {estudiante.apellidos}")
        print(f"(Estudiante): {estudiante.identificacion}. Estado de aprobación en {evaluacion_academica.unidad_curricular.nombre}: {estado_final.value}")


class ObservadorInformeGeneral(IObservadorDeEvaluacion):
    def actualizar(self, evaluacion_academica: EvaluacionAcademica):
    #Reacciona al cierre de la evaluación académica para enviar los datos de rendimiento hacia el procesamiento de informes.
        if evaluacion_academica._estado_de_aprobacion != EstadoDeAprobacion.PENDIENTE:
            resumen = evaluacion_academica.obtener_resumen_de_evaluacion()
            print(f"(Informe general) Estudiante: {resumen['Estudiante']}. Nota Final: {resumen['Nota final']}")