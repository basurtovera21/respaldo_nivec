from datetime import date

from poo.clases.enums.tipo_de_informe import TipoDeInforme
from poo.clases.enums.estado_de_informe import EstadoDeInforme
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo

from poo.clases.interfaces.i_informe_institucional import IInformeInstitucional
from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion


class InformeGeneral(IInformeInstitucional):
    """
    Gestiona el ciclo de vida de un informe institucional de nivelación.

    Implementa IInformeInstitucional.

    Uso actual desde Django:
        informe_poo = InformeGeneral(codigo, periodo_poo, tipo)
        resultado = informe_poo.emitir_informe_de_nivelacion()

    Regla de negocio:
        Un informe solo puede emitirse si el periodo asociado está cerrado.
    """

    def __init__(self, codigo_de_informe: str, periodo_academico: PeriodoDeNivelacion,
                 tipo_de_informe: TipoDeInforme):
        self._codigo_de_informe = codigo_de_informe
        self._periodo_academico = periodo_academico
        self._tipo_de_informe = tipo_de_informe
        self._estado_de_informe = EstadoDeInforme.BORRADOR
        self._fecha_de_emision = None

    @property
    def codigo_de_informe(self):
        return self._codigo_de_informe

    @property
    def periodo_academico(self):
        return self._periodo_academico

    @property
    def tipo_de_informe(self):
        return self._tipo_de_informe

    @property
    def estado_de_informe(self):
        return self._estado_de_informe

    @property
    def fecha_de_emision(self):
        return self._fecha_de_emision

    def emitir_informe_de_nivelacion(self) -> bool:
        """
        Emite el informe cambiando su estado a Revisión.
        Solo se permite si el periodo asociado está cerrado.
        """
        if self._periodo_academico.estado != EstadoDePeriodo.CERRADO:
            return False
        self._fecha_de_emision = date.today()
        self._estado_de_informe = EstadoDeInforme.REVISION
        return True
