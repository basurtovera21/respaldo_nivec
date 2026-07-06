"""
Servicio de depuración y validación de datos externos (matrices Excel/CSV).

Aplica una cadena de criterios de filtro (Strategy) para separar los registros
válidos de aquellos con observaciones (registros inválidos o inconsistentes).

Patrón aplicado: Strategy (via ICriterioFiltro)
    Cada criterio es una estrategia de validación intercambiable.
    El depurador no conoce los detalles de cada validación, solo invoca
    es_valido() en cada criterio configurado.

Criterios disponibles:
    - CriterioCedulaFormato: Valida formato numérico de cédula (≥ 5 dígitos)
    - CriterioConsistenteDeHoras: Valida que sincrónicas + asincrónicas = totales

Uso desde Django:
    from poo.clases.servicios.depurador_de_sincronizacion import DepuradorDeSincronizacion
    from poo.clases.criterios_filtro.criterio_cedula_formato import CriterioCedulaFormato

    depurador = DepuradorDeSincronizacion([CriterioCedulaFormato()])
    depurador.procesar_matriz_externa(registros)
    # depurador.registros_validos → lista de registros que pasaron todos los criterios
    # depurador.registros_con_observaciones → lista de registros rechazados

Principios:
    - SRP: Solo se encarga de filtrar registros usando criterios inyectados
    - OCP: Nuevos criterios se agregan sin modificar este servicio
    - DIP: Depende de la abstracción ICriterioFiltro, no de implementaciones concretas
"""

from poo.clases.interfaces.i_criterio_filtro import ICriterioFiltro


class DepuradorDeSincronizacion:
    """
    Servicio que procesa una matriz de datos externos aplicando criterios
    de validación configurables para separar registros válidos de observados.
    """

    def __init__(self, criterios: list):
        """
        Args:
            criterios: Lista de instancias que implementan ICriterioFiltro.
                       Se aplican en orden; el primer criterio que falle
                       marca el registro como observado.
        """
        self._criterios = criterios
        self._registros_validos = []
        self._registros_con_observaciones = []

    # ── Properties ──

    @property
    def registros_validos(self):
        """Registros que pasaron todos los criterios de validación."""
        return self._registros_validos

    @property
    def registros_con_observaciones(self):
        """Registros que fallaron al menos un criterio de validación."""
        return self._registros_con_observaciones

    # ── Procesamiento ──

    def procesar_matriz_externa(self, matriz_externa: list):
        """
        Procesa una lista de registros (diccionarios) aplicando cada criterio.

        Un registro es válido si pasa TODOS los criterios configurados.
        Si falla en alguno, se clasifica como observado y se detiene la
        validación de ese registro (fail-fast).

        Args:
            matriz_externa: Lista de diccionarios con los datos a validar
        """
        self._registros_validos = []
        self._registros_con_observaciones = []

        for registro in matriz_externa:
            es_valido = True
            for criterio in self._criterios:
                if not criterio.es_valido(registro):
                    es_valido = False
                    break

            if es_valido:
                self._registros_validos.append(registro)
            else:
                self._registros_con_observaciones.append(registro)

    # ── Resumen ──

    def obtener_resumen_depuracion(self) -> dict:
        """
        Retorna un resumen cuantitativo del proceso de depuración.

        Returns:
            Diccionario con conteo de registros válidos y observados
        """
        return {
            "Registros válidos": len(self._registros_validos),
            "Registros con observaciones": len(self._registros_con_observaciones),
        }
