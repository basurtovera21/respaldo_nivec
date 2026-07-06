"""
Patrón creacional: Prototype

Define la interfaz para objetos que pueden crear copias de sí mismos.
En este sistema, MallaCurricular implementa IClonable para permitir
crear nuevas versiones preservando toda la estructura de unidades.

Ventaja del patrón:
    Evita reconstruir objetos complejos desde cero. En lugar de crear
    una nueva malla vacía y copiar unidad por unidad, se clona toda
    la estructura en una operación.
"""

from abc import ABCMeta, abstractmethod


class IClonable(metaclass=ABCMeta):
    """
    Interfaz abstracta para el patrón Prototype.
    Los objetos que la implementen deben poder crear copias de sí mismos.
    """

    @abstractmethod
    def clonar(self, *args, **kwargs):
        """
        Crea y retorna una copia profunda del objeto actual.
        Los argumentos permiten personalizar la copia (ej: nuevo código, versión).
        """
        pass
