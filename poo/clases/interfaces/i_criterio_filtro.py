"""
Patrón de comportamiento: Strategy (para validación/filtrado)

Define la interfaz que deben implementar todos los criterios de filtro
usados por el DepuradorDeSincronizacion para validar registros externos.

Implementaciones concretas:
    - CriterioCedulaFormato: Valida formato numérico de cédula (≥ 5 dígitos)
    - CriterioConsistenteDeHoras: Valida que sincrónicas + asincrónicas = totales

Principios:
    - ISP: Interfaz mínima (solo es_valido)
    - OCP: Nuevos criterios se crean sin modificar el depurador
    - DIP: El depurador depende de esta abstracción, no de implementaciones
"""

from abc import ABCMeta, abstractmethod


class ICriterioFiltro(metaclass=ABCMeta):
    """
    Interfaz abstracta para criterios de filtrado de datos.

    Cada criterio concreto evalúa un aspecto específico de un registro
    (diccionario) y determina si es válido según su regla particular.
    """

    @abstractmethod
    def es_valido(self, registro: dict) -> bool:
        """
        Evalúa si un registro cumple con el criterio de validación.

        Args:
            registro: Diccionario con los datos del registro a validar

        Returns:
            True si el registro es válido según este criterio
        """
        pass
