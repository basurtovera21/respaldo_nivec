from interfaces.i_criterio_filtro import ICriterioFiltro


class CriterioPeriodoValido(ICriterioFiltro):
    def __init__(self, periodo_activo: str):
        self.periodo_activo = periodo_activo

    def es_valido(self, registro: dict):
        return registro.get("periodo") == self.periodo_activo