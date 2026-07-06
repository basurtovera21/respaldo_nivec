from datetime import date

from poo.clases.enums.tipo_de_informe import TipoDeInforme
from poo.clases.enums.estado_de_informe import EstadoDeInforme
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo
from poo.clases.enums.estado_de_aprobacion import EstadoDeAprobacion

from poo.clases.interfaces.i_informe_institucional import IInformeInstitucional
from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion
from poo.clases.cohorte_de_matricula import CohorteDeMatricula


class InformeGeneral(IInformeInstitucional):
    """
    Gestiona informes institucionales del periodo de nivelación.

    Implementa IInformeInstitucional (emitir_informe_de_nivelacion).

    Uso desde Django (v_procesos_academicos.py):
        informe_poo = InformeGeneral(codigo, periodo_poo, tipo)
        resultado = informe_poo.emitir_informe_de_nivelacion()

    Métodos disponibles para futura implementación:
        - agregar_cohorte_de_matricula(cohorte)
        - consolidar_estadisticas_institucionales(evaluaciones)
        - estimar_tasas_de_aprobacion(evaluaciones)
    """

    def __init__(self, codigo_de_informe: str, periodo_academico: PeriodoDeNivelacion,
                 tipo_de_informe: TipoDeInforme):
        self._codigo_de_informe = codigo_de_informe
        self._periodo_academico = periodo_academico
        self._tipo_de_informe = tipo_de_informe
        self._estado_de_informe = EstadoDeInforme.BORRADOR
        self._cohortes = []
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
        """Emite el informe si el periodo está cerrado."""
        if self._periodo_academico.estado != EstadoDePeriodo.CERRADO:
            return False
        self._fecha_de_emision = date.today()
        self._estado_de_informe = EstadoDeInforme.REVISION
        return True

    def agregar_cohorte_de_matricula(self, cohorte: CohorteDeMatricula) -> bool:
        """Agrega una cohorte al informe (para futura implementación)."""
        if not isinstance(cohorte, CohorteDeMatricula):
            return False
        if cohorte in self._cohortes:
            return False
        self._cohortes.append(cohorte)
        return True

    def obtener_total_matriculados(self) -> int:
        """Suma el total de matriculados de todas las cohortes asociadas."""
        total = 0
        for cohorte in self._cohortes:
            total += cohorte.calcular_total_matriculados()
        return total

    def consolidar_estadisticas_institucionales(self, evaluaciones: list) -> dict:
        """Consolida estadísticas por carrera (para futura implementación)."""
        estadisticas = {}
        for cohorte in self._cohortes:
            nombre = cohorte.carrera_registrada.nombre if cohorte.carrera_registrada else "Sin carrera"
            if nombre not in estadisticas:
                estadisticas[nombre] = {"aprobados": 0, "reprobados": 0, "retirados": 0, "anulados": 0}

        for evaluacion in evaluaciones:
            carrera = evaluacion.estudiante.carrera_registrada
            nombre = carrera.nombre if hasattr(carrera, 'nombre') else str(carrera)
            if nombre in estadisticas:
                estado = evaluacion._estado_de_aprobacion
                if estado == EstadoDeAprobacion.APROBADO:
                    estadisticas[nombre]["aprobados"] += 1
                elif estado == EstadoDeAprobacion.REPROBADO:
                    estadisticas[nombre]["reprobados"] += 1
                elif estado == EstadoDeAprobacion.RETIRADO:
                    estadisticas[nombre]["retirados"] += 1
                elif estado == EstadoDeAprobacion.ANULADO:
                    estadisticas[nombre]["anulados"] += 1

        return estadisticas

    def estimar_tasas_de_aprobacion(self, evaluaciones: list) -> dict:
        """Calcula tasas de aprobación/reprobación (para futura implementación)."""
        total = len(evaluaciones)
        if total == 0:
            return {"tasa_aprobacion": 0.0, "tasa_reprobacion": 0.0, "tasa_retiros": 0.0}

        aprobados = sum(1 for e in evaluaciones if e._estado_de_aprobacion == EstadoDeAprobacion.APROBADO)
        reprobados = sum(1 for e in evaluaciones if e._estado_de_aprobacion == EstadoDeAprobacion.REPROBADO)
        retiros = sum(1 for e in evaluaciones if e._estado_de_aprobacion in (EstadoDeAprobacion.RETIRADO, EstadoDeAprobacion.ANULADO))

        return {
            "tasa_aprobacion": round(aprobados / total * 100, 2),
            "tasa_reprobacion": round(reprobados / total * 100, 2),
            "tasa_retiros": round(retiros / total * 100, 2),
        }
