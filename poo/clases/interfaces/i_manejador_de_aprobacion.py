"""
Patrón de comportamiento: Chain of Responsibility

Al recibir una solicitud de verificación de aprobación, cada manejador
decide si la procesa (cambia el estado) o si la pasa al siguiente
manejador de la cadena.

Cadena actual:
    ManejadorEstadoInactivo → ManejadorAsistencia → ManejadorCalificacion

Cada manejador tiene una responsabilidad única (SRP):
    - ManejadorEstadoInactivo: Verifica si el estudiante está RETIRADO/ANULADO
    - ManejadorAsistencia: Verifica el porcentaje mínimo de asistencia
    - ManejadorCalificacion: Verifica la nota final contra el criterio de aprobación
"""

from abc import ABCMeta, abstractmethod


class IManejadorDeAprobacion(metaclass=ABCMeta):
    """
    Interfaz abstracta para los manejadores de la cadena de aprobación.

    Cada manejador concreto recibe una referencia al siguiente manejador
    y decide si procesa la evaluación o la delega.
    """

    def __init__(self, siguiente=None):
        """
        Args:
            siguiente: Referencia al siguiente manejador de la cadena (o None si es el último)
        """
        self._siguiente = siguiente

    @property
    def siguiente(self):
        """Acceso al siguiente manejador de la cadena."""
        return self._siguiente

    @abstractmethod
    def manejar(self, evaluacion):
        """
        Procesa la evaluación o la delega al siguiente manejador.

        Args:
            evaluacion: Instancia de EvaluacionAcademica a procesar
        
        Returns:
            EstadoDeAprobacion resultante
        """
        pass
