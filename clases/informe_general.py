from datetime import date

#Enums
from clases.enums.formato_de_exportacion import FormatoDeExportacion
from clases.enums.tipo_de_informe import TipoDeInforme
from clases.enums.estado_de_informe import EstadoDeInforme

#Interface
from clases.i_informe_institucional import IInformeInstitucional

from clases.periodo_de_nivelacion import PeriodoDeNivelacion
from clases.cohorte_de_matricula import CohorteDeMatricula


class InformeGeneral(IInformeInstitucional): #Interfaz
    def __init__(self, codigo_de_informe, periodo_academico: PeriodoDeNivelacion, tipo_de_informe: TipoDeInforme):
        self.codigo_de_informe = codigo_de_informe
        self.periodo_academico = periodo_academico
        self.tipo_de_informe = tipo_de_informe #Instancia
        self._estado_de_informe = EstadoDeInforme.BORRADOR
        self._cohortes = [] # Lista de instancias CohorteDeMatricula
        self._fecha_de_emision  = None #datetime.date


    def emitir_informe_de_nivelacion(self):
        from clases.enums.estado_de_periodo import EstadoDePeriodo
        from clases.enums.estado_de_informe import EstadoDeInforme

        if self.periodo_academico._estado != EstadoDePeriodo.CERRADO:
            print(f"[Informe general] No se puede emitir el informe: El periodo no ha sido cerrado.")
            return
        
        total_matriculados = 0
        for cohorte in self._cohortes:
            total_matriculados += cohorte.calcular_total_matriculados()
            
        print(f"[Informe general] Emitiendo informe: {self.codigo_de_informe}")
        print(f"Periodo académico: {self.periodo_academico.periodo}")
        print(f"Tipo de informe: {self.tipo_de_informe.value}")
        print(f"Total matriculados consolidados: {total_matriculados}")

        self._fecha_de_emision  = date.today()
        self._estado_de_informe = EstadoDeInforme.REVISION
        print(f"Fecha de emisión: {self._fecha_de_emision}")
        print(f"Estado actualizado: {self._estado_de_informe.value}")
        
    def exportar_consolidado_de_estudiantes(self, formato_de_exportacion):
        from clases.enums.formato_de_exportacion import FormatoDeExportacion

        nombre_de_archivo = f"{self.codigo_de_informe}_{self.tipo_de_informe.value}"

        if formato_de_exportacion == FormatoDeExportacion.PDF:
            nombre_de_archivo += ".pdf"
            print(f"[Informe general] Exportando como PDF ({nombre_de_archivo})")
            print(f"Consolidado del periodo {self.periodo_academico.periodo}")
            
        elif formato_de_exportacion == FormatoDeExportacion.EXCEL:
            nombre_de_archivo += ".xlsx"
            print(f"[Informe general] Exportando como Excel ({nombre_de_archivo})")
            print(f"Consolidado del periodo {self.periodo_academico.periodo}")

        else:
            print(f"[Informe general] Formato no soportado: {formato_de_exportacion}")
            return

        print(f"El archivo ha sido generado correctamente: {nombre_de_archivo}")
            
    def procesar_retiros_y_anulaciones(self):
        pass
    def estimar_tasas_de_aprobacion(self): #Retorna dict
        pass