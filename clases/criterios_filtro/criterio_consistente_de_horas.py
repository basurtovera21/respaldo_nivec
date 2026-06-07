from interfaces.i_criterio_filtro import ICriterioFiltro


class CriterioConsistentesDeHoras(ICriterioFiltro):
    def es_valido(self, registro: dict):
        horas_totales = registro.get("horas_totales", 0)
        horas_sincronicas = registro.get("horas_sincronicas", 0)
        horas_asincronicas = registro.get("horas_asincronicas", 0)

        return (horas_sincronicas + horas_asincronicas) == horas_totales