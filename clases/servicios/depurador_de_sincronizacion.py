#criterios_filtro
from interfaces.i_criterio_filtro import ICriterioFiltro


class DepuradorDeSincronizacion:
    def __init__(self, criterios: list[ICriterioFiltro]):
        self.criterios = criterios
        self.registros_validos = []
        self.registros_con_observaciones = []


    def procesar_matriz_externa(self, matriz_externa: list):
        self.registros_validos = []
        self.registros_con_observaciones = []
        
        for registro in matriz_externa:
            es_valido = True
            for criterio in self.criterios:
                if not criterio.es_valido(registro):
                    es_valido = False
                    break

            if es_valido:
                self.registros_validos.append(registro)
                
            else:
                self.registros_con_observaciones.append(registro)


    def obtener_resumen_depuracion(self):
        return {
            "Registros válidos": len(self.registros_validos),
            "Registros con observaciones": len(self.registros_con_observaciones)
        }