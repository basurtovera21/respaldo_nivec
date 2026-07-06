"""
Servicio de procesamiento y exportación de informes institucionales.

Genera archivos en distintos formatos (PDF, Excel) a partir de un
InformeGeneral. Actúa como el componente de exportación del subsistema
de informes dentro del Facade.

Nota: En esta implementación los métodos de generación retornan True
simulando la creación del archivo. En producción, Django maneja la
exportación real (openpyxl para Excel, etc.) en academico/services.py.

Principios:
    - SRP: Solo se encarga de la lógica de exportación de informes
    - OCP: Nuevos formatos se agregan como nuevos métodos _generar_archivo_*
"""

from poo.clases.enums.formato_de_exportacion import FormatoDeExportacion
from poo.clases.informe_general import InformeGeneral


class ProcesadorDeInforme:
    """
    Servicio que exporta informes institucionales en distintos formatos.

    Formatos soportados:
        - PDF: Documento formal para impresión/archivo
        - Excel: Hoja de cálculo para análisis de datos
    """

    def exportar_consolidado(self, informe_general: InformeGeneral,
                              formato_de_exportacion: FormatoDeExportacion):
        """
        Exporta un informe en el formato especificado.

        Args:
            informe_general: Instancia del informe a exportar
            formato_de_exportacion: Formato deseado (PDF o EXCEL)

        Returns:
            True si la exportación fue exitosa, False si el formato no es soportado
        """
        nombre_base = (
            f"{informe_general.codigo_de_informe}_"
            f"{informe_general.tipo_de_informe.value}"
        )

        if formato_de_exportacion == FormatoDeExportacion.PDF:
            return self._generar_archivo_pdf(f"{nombre_base}.pdf", informe_general)

        if formato_de_exportacion == FormatoDeExportacion.EXCEL:
            return self._generar_archivo_excel(f"{nombre_base}.xlsx", informe_general)

        return False

    def _generar_archivo_pdf(self, nombre_de_archivo: str,
                              informe_general: InformeGeneral) -> bool:
        """
        Genera un archivo PDF del informe.

        En producción, la generación real se maneja en Django services.py
        usando librerías como ReportLab o WeasyPrint.
        """
        return True

    def _generar_archivo_excel(self, nombre_de_archivo: str,
                                informe_general: InformeGeneral) -> bool:
        """
        Genera un archivo Excel del informe.

        En producción, la generación real se maneja en Django services.py
        usando openpyxl.
        """
        return True
