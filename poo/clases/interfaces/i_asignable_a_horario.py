"""
Interfaz para entidades que pueden ser asignadas a un horario (bloques de tiempo).

Actualmente implementada por:
    - Docente: Puede ser responsable de sesiones de horario

Principio ISP:
    Solo exige las propiedades mínimas necesarias para identificar
    al responsable de un bloque horario (nombres y apellidos).
"""

from abc import ABCMeta, abstractmethod


class IAsignableAHorario(metaclass=ABCMeta):
    """
    Interfaz que deben implementar las entidades que pueden vincularse
    como responsables de una sesión de horario.
    """

    @property
    @abstractmethod
    def nombres(self):
        """Nombres del responsable del horario."""
        pass

    @property
    @abstractmethod
    def apellidos(self):
        """Apellidos del responsable del horario."""
        pass
