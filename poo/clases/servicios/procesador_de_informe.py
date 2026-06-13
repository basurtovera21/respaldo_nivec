#InformeGeneral

#Enums
from poo.clases.enums.formato_de_exportacion import FormatoDeExportacion

#Clases
from poo.clases.informe_general import InformeGeneral


class ProcesadorDeInforme:
    def exportar_consolidado(self, informe_general: InformeGeneral, formato_de_exportacion: FormatoDeExportacion):
        nombre_base = f"{informe_general.codigo_de_informe}_{informe_general.tipo_de_informe.value}"

        if formato_de_exportacion == FormatoDeExportacion.PDF:
            return self._generar_archivo_pdf(f"{nombre_base}.pdf", informe_general)

        if formato_de_exportacion == FormatoDeExportacion.EXCEL:
            return self._generar_archivo_excel(f"{nombre_base}.xlsx", informe_general)

        return False


    def _generar_archivo_pdf(self, nombre_de_archivo: str, informe_general: InformeGeneral):
        return True


    def _generar_archivo_excel(self, nombre_de_archivo: str, informe_general: InformeGeneral):
        return True