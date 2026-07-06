"""
Servicio de distribución automática de estudiantes a paralelos.

Algoritmo de distribución:
    Para cada estudiante, se busca el paralelo con menor ocupación
    que tenga cupo disponible. Esto garantiza una distribución
    equilibrada entre paralelos.

    Si no hay paralelos con cupo, el estudiante queda sin asignar.

Uso desde Django (vía Facade):
    facade = CentroDeOperacionAcademica()
    no_asignados = facade.distribuir_estudiantes(paralelos_poo, estudiantes_list)

Principios:
    - SRP: Solo se encarga de la lógica de distribución
    - OCP: El criterio de selección puede extenderse sobreescribiendo _encontrar_mejor_paralelo
"""


class DistribuidorDeEstudiantes:
    """
    Servicio que distribuye una lista de estudiantes en paralelos
    usando el criterio de menor carga (balanceo).
    """

    def __init__(self, lista_paralelos: list):
        self._paralelos = lista_paralelos

    # ── Properties ──

    @property
    def paralelos(self):
        """Lista de paralelos disponibles para distribución."""
        return self._paralelos

    @paralelos.setter
    def paralelos(self, valor: list):
        """Permite reasignar la lista de paralelos (usado por el Facade)."""
        self._paralelos = valor

    # ── Distribución ──

    def distribuir(self, lista_estudiantes: list) -> list:
        """
        Distribuye estudiantes en los paralelos configurados.

        Algoritmo:
            1. Para cada estudiante, busca el paralelo con menor ocupación
            2. Si hay paralelo con cupo → vincula al estudiante
            3. Si no hay cupo → lo agrega a la lista de no asignados

        Args:
            lista_estudiantes: Lista de instancias Estudiante a distribuir

        Returns:
            Lista de estudiantes que no pudieron ser asignados (sin cupo disponible)
        """
        estudiantes_no_asignados = []

        for estudiante in lista_estudiantes:
            mejor_paralelo = self._encontrar_mejor_paralelo()
            if mejor_paralelo:
                mejor_paralelo.vincular_estudiante(estudiante)
            else:
                estudiantes_no_asignados.append(estudiante)

        return estudiantes_no_asignados

    def _encontrar_mejor_paralelo(self):
        """
        Selecciona el paralelo con menor ocupación que tenga cupo disponible.

        Criterio: min(estudiantes_matriculados) entre paralelos con cupo.

        Returns:
            Instancia de Paralelo con menor carga, o None si no hay cupo
        """
        paralelos_con_cupo = [p for p in self._paralelos if p.tiene_cupo_disponible()]

        if not paralelos_con_cupo:
            return None

        return min(paralelos_con_cupo, key=lambda p: p.total_estudiantes_matriculados)
