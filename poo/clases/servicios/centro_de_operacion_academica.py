"""
Patrón de diseño estructural: Facade (Fachada)

CentroDeOperacionAcademica simplifica el acceso a los subsistemas complejos
de la capa POO, proporcionando una interfaz unificada para Django.

Subsistemas encapsulados:
    1. Estudiantes: matrícula, retiro, anulación
    2. Docentes: carga horaria, habilitación, validación de asignación
    3. Distribución: asignación automática de estudiantes a paralelos
    4. Evaluación: registro y verificación de calificaciones
    5. Periodos: control del ciclo de vida del periodo de nivelación
    6. Cohortes: administración de cohortes de matrícula
    7. Informes: emisión y exportación de reportes institucionales

Principios:
    - Facade: Punto de entrada único que oculta la complejidad interna
    - SRP: Cada subsistema mantiene su propia responsabilidad
    - DIP: Depende de abstracciones (interfaces), no de implementaciones concretas
"""

# Servicios internos
from poo.clases.servicios.distribuidor_de_estudiantes import DistribuidorDeEstudiantes
from poo.clases.servicios.procesador_de_informe import ProcesadorDeInforme

# Clases de dominio
from poo.clases.usuarios.estudiante import Estudiante
from poo.clases.usuarios.docente import Docente
from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion
from poo.clases.evaluacion_academica import EvaluacionAcademica
from poo.clases.informe_general import InformeGeneral
from poo.clases.cohorte_de_matricula import CohorteDeMatricula

# Enums
from poo.clases.enums.formato_de_exportacion import FormatoDeExportacion


class CentroDeOperacionAcademica:
    """
    Fachada principal del sistema académico de nivelación.

    Proporciona una interfaz simplificada para que la capa Django (services.py)
    interactúe con los objetos de dominio sin conocer sus detalles internos.

    Uso desde Django:
        facade = CentroDeOperacionAcademica()
        facade.distribuir_estudiantes(paralelos, estudiantes)
        facade.iniciar_periodo(periodo_poo)
        facade.validar_asignacion_docente(docente_poo, paralelo_poo, horas)
    """

    def __init__(self):
        self._distribuidor = DistribuidorDeEstudiantes([])
        self._procesador = ProcesadorDeInforme()

    # ══════════════════════════════════════════════════════════
    # SUBSISTEMA 1: ESTUDIANTES
    # ══════════════════════════════════════════════════════════

    def formalizar_matricula(self, estudiante: Estudiante):
        """Formaliza la matrícula de un estudiante (ASPIRANTE → MATRICULADO)."""
        return estudiante.formalizar_matricula()

    def solicitar_retiro(self, estudiante: Estudiante):
        """Procesa la solicitud de retiro de un estudiante (MATRICULADO → RETIRADO)."""
        return estudiante.solicitar_retiro()

    def anular_matricula(self, estudiante: Estudiante):
        """Anula la matrícula de un estudiante (→ ANULADO)."""
        estudiante.anular_matricula()

    # ══════════════════════════════════════════════════════════
    # SUBSISTEMA 2: DOCENTES
    # ══════════════════════════════════════════════════════════

    def inhabilitar_docente(self, docente: Docente):
        """Inhabilita a un docente (ACTIVO → INACTIVO)."""
        docente.inhabilitar()

    def habilitar_docente(self, docente: Docente):
        """Habilita a un docente previamente inhabilitado (INACTIVO → ACTIVO)."""
        docente.habilitar()

    def obtener_carga_academica(self, docente: Docente) -> dict:
        """Retorna el resumen de carga académica del docente."""
        return docente.visualizar_carga_academica()

    def verificar_disponibilidad_horaria(self, docente: Docente, horario) -> bool:
        """Verifica si el docente tiene disponibilidad para un horario específico."""
        return docente.verificar_disponibilidad_horaria(horario)

    def validar_asignacion_docente(self, docente: Docente, paralelo, horas_de_la_unidad: float) -> dict:
        """
        Validación completa para asignar un docente a un paralelo.

        Verifica: estado activo, disponibilidad horaria, carga máxima.

        Returns:
            {"ok": True} si la asignación es válida
            {"ok": False, "motivo": str, ...} si no es válida
        """
        return docente.validar_asignacion_a_paralelo(paralelo, horas_de_la_unidad)

    # ══════════════════════════════════════════════════════════
    # SUBSISTEMA 3: DISTRIBUCIÓN DE ESTUDIANTES
    # ══════════════════════════════════════════════════════════

    def distribuir_estudiantes(self, paralelos: list, estudiantes: list) -> list:
        """
        Distribuye estudiantes en paralelos usando el algoritmo de menor carga.

        El distribuidor asigna cada estudiante al paralelo con menor ocupación
        que tenga cupo disponible.

        Args:
            paralelos: Lista de instancias Paralelo (POO) con cupo
            estudiantes: Lista de instancias Estudiante (POO) a distribuir

        Returns:
            Lista de estudiantes que no pudieron ser asignados (sin cupo)
        """
        self._distribuidor.paralelos = paralelos
        return self._distribuidor.distribuir(estudiantes)

    # ══════════════════════════════════════════════════════════
    # SUBSISTEMA 4: EVALUACIÓN ACADÉMICA
    # ══════════════════════════════════════════════════════════

    def registrar_evaluacion(self, evaluacion: EvaluacionAcademica,
                             parcial_1: float, parcial_2: float,
                             porcentaje_asistencia: float):
        """
        Registra calificaciones y determina el estado de aprobación.

        Flujo completo: registrar notas → registrar asistencia →
        calcular nota final → verificar aprobación (Chain of Responsibility).

        Returns:
            EstadoDeAprobacion resultante
        """
        evaluacion.registrar_calificacion(1, parcial_1)
        evaluacion.registrar_calificacion(2, parcial_2)
        evaluacion.registrar_asistencia_final(porcentaje_asistencia)
        evaluacion.calcular_nota_final()
        return evaluacion.verificar_aprobacion()

    def obtener_acta_de_paralelo(self, evaluaciones: list) -> list:
        """
        Genera el acta de evaluación de un paralelo completo.

        Args:
            evaluaciones: Lista de instancias EvaluacionAcademica

        Returns:
            Lista de resúmenes (diccionarios) por estudiante
        """
        return EvaluacionAcademica.registrar_evaluacion_de_paralelo(evaluaciones)

    # ══════════════════════════════════════════════════════════
    # SUBSISTEMA 5: PERIODOS DE NIVELACIÓN
    # ══════════════════════════════════════════════════════════

    def iniciar_periodo(self, periodo: PeriodoDeNivelacion) -> bool:
        """Inicia un periodo (PLANIFICACIÓN → EN CURSO)."""
        return periodo.iniciar_periodo_de_nivelacion()

    def finalizar_periodo(self, periodo: PeriodoDeNivelacion) -> bool:
        """Finaliza un periodo (EN CURSO/EVALUACIÓN → CERRADO)."""
        return periodo.finalizar_periodo_de_nivelacion()

    def obtener_matriz_de_horarios(self, periodo: PeriodoDeNivelacion, paralelos: list):
        """Genera la matriz consolidada de horarios del periodo."""
        return periodo.generar_matriz_de_horarios(paralelos)

    # ══════════════════════════════════════════════════════════
    # SUBSISTEMA 6: COHORTES DE MATRÍCULA
    # ══════════════════════════════════════════════════════════

    def registrar_estudiante_en_cohorte(self, cohorte: CohorteDeMatricula,
                                         estudiante: Estudiante):
        """Registra un estudiante matriculado en una cohorte."""
        return cohorte.registrar_estudiante_matriculado(estudiante)

    def obtener_estadisticas_de_cohorte(self, cohorte: CohorteDeMatricula) -> dict:
        """Retorna las estadísticas de registro de una cohorte."""
        return cohorte.obtener_estadisticas_de_registro()

    # ══════════════════════════════════════════════════════════
    # SUBSISTEMA 7: INFORMES INSTITUCIONALES
    # ══════════════════════════════════════════════════════════

    def emitir_informe(self, informe: InformeGeneral):
        """Emite un informe de nivelación (cambia su estado a EMITIDO)."""
        return informe.emitir_informe_de_nivelacion()

    def exportar_informe(self, informe: InformeGeneral, formato: FormatoDeExportacion):
        """
        Exporta un informe en el formato especificado (PDF, Excel).
        Delega al ProcesadorDeInforme.
        """
        return self._procesador.exportar_consolidado(informe, formato)

    def consolidar_estadisticas(self, informe: InformeGeneral, evaluaciones: list):
        """Consolida las estadísticas institucionales del informe."""
        return informe.consolidar_estadisticas_institucionales(evaluaciones)

    def estimar_tasas(self, informe: InformeGeneral, evaluaciones: list):
        """Estima las tasas de aprobación del periodo."""
        return informe.estimar_tasas_de_aprobacion(evaluaciones)
