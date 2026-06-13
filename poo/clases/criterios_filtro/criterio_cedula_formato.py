from poo.clases.interfaces.i_criterio_filtro import ICriterioFiltro


class CriterioCedulaFormato(ICriterioFiltro):
    def es_valido(self, registro: dict):
        numero_de_cedula = str(registro.get("cedula", ""))
        
        return numero_de_cedula.isdigit() and len(numero_de_cedula) == 10