#Interfaz
from abc import ABCMeta
from abc import abstractmethod

#Enum
from clases.enums.formato_de_exportacion import FormatoDeExportacion


class IInformeInstitucional(metaclass = ABCMeta):
    @abstractmethod
    def emitir_informe_de_nivelacion(self):
        pass
    
    @abstractmethod
    def exportar_consolidado_de_estudiantes(self, formato_de_exportacion: FormatoDeExportacion):
        pass