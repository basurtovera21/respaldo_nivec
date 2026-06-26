import unicodedata

from poo.clases.interfaces.i_criterio_filtro import ICriterioFiltro

class CriterioCedulaFormato(ICriterioFiltro):
    @staticmethod
    def _normalizar(texto):
        texto = str(texto or "").strip().lower()
        return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

    def es_valido(self, registro: dict):
        tipo_de_identificacion = self._normalizar(registro.get("tipo_de_identificacion", ""))
        numero_de_cedula = str(registro.get("cedula", ""))
        if tipo_de_identificacion != "cedula":
            return True

        return numero_de_cedula.isdigit() and len(numero_de_cedula) == 10
