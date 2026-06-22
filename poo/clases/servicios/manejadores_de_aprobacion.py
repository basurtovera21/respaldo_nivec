from poo.clases.interfaces.i_manejador_de_aprobacion import IManejadorDeAprobacion
from poo.clases.enums.estado_de_aprobacion import EstadoDeAprobacion


# Validación de estudiante con estado de aprobación RETIRADO o ANULADO
class ManejadorEstadoInactivo(IManejadorDeAprobacion):
    def manejar(self, evaluacion_academica: 'EvaluacionAcademica'):
        from poo.clases.evaluacion_academica import EvaluacionAcademica
        #Si está RETIRADO o ANULADO, termina la cadena y retorna ese estado
        if evaluacion_academica._estado_de_aprobacion in (EstadoDeAprobacion.RETIRADO, EstadoDeAprobacion.ANULADO):
            return evaluacion_academica._estado_de_aprobacion
        
        #Si no, pasa al siguiente
        if self.siguiente:
            return self.siguiente.manejar(evaluacion_academica)
        return evaluacion_academica._estado_de_aprobacion

#Validación del porcentaje de asistencia
class ManejadorAsistencia(IManejadorDeAprobacion):
    def manejar(self, evaluacion_academica: 'EvaluacionAcademica'):
        from poo.clases.evaluacion_academica import EvaluacionAcademica
        if evaluacion_academica._porcentaje_asistencia < evaluacion_academica.unidad_curricular.porcentaje_minimo_asistencia:
            evaluacion_academica._estado_de_aprobacion = EstadoDeAprobacion.REPROBADO
            evaluacion_academica._observacion = "Reprobado por porcentaje de asistencia insuficiente"
            return evaluacion_academica._estado_de_aprobacion
        
        #Si cumple asistencia, pasa a validar la nota final
        if self.siguiente:
            return self.siguiente.manejar(evaluacion_academica)
        return evaluacion_academica._estado_de_aprobacion

#Validación de la nota final
class ManejadorCalificacion(IManejadorDeAprobacion):
    def manejar(self, evaluacion_academica: 'EvaluacionAcademica'):
        from poo.clases.evaluacion_academica import EvaluacionAcademica
        if evaluacion_academica._nota_final >= evaluacion_academica.unidad_curricular.criterio_de_aprobacion:
            evaluacion_academica._estado_de_aprobacion = EstadoDeAprobacion.APROBADO
            evaluacion_academica._observacion = "Aprobado"
        else:
            evaluacion_academica._estado_de_aprobacion = EstadoDeAprobacion.REPROBADO
            evaluacion_academica._observacion = "Reprobado por calificación insuficiente"
            
        if self.siguiente:
            return self.siguiente.manejar(evaluacion_academica)
        return evaluacion_academica._estado_de_aprobacion