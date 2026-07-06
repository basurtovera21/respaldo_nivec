from poo.clases.enums.jornada import Jornada
from poo.clases.enums.modalidad import Modalidad

from poo.clases.usuarios.docente import Docente
from poo.clases.usuarios.estudiante import Estudiante

from poo.clases.horario import Horario


class Paralelo:
    """
    Entidad que representa un grupo de estudiantes asignados a una unidad curricular
    dentro de un periodo de nivelación, con jornada, docente y horarios definidos.

    Responsabilidades:
        - Gestionar la vinculación/desvinculación de estudiantes y docente
        - Controlar la capacidad máxima de cupo
        - Administrar y validar horarios (conflictos, horas agendadas)
        - Proveer resumen de información del paralelo

    Principios:
        - SRP: Solo gestiona la lógica de un paralelo (cupo, horarios, asignaciones)
        - Encapsulación: Docente y estudiantes protegidos, horarios accesibles para iteración

    Reglas de negocio:
        - Capacidad por defecto: 35 estudiantes
        - Rango de capacidad válido: 20-50 (validado en forms.py)
        - Solo un docente responsable a la vez
        - No se permiten conflictos horarios dentro del mismo paralelo
        - Las horas agendadas no pueden exceder las horas sincrónicas requeridas
    """

    # ── Constantes de negocio ──
    CAPACIDAD_MINIMA = 20
    CAPACIDAD_MAXIMA_PERMITIDA = 50
    CAPACIDAD_MAXIMA_PREDETERMINADA = 35

    def __init__(self, codigo_de_paralelo: str, nombre: str, jornada: Jornada,
                 modalidad: Modalidad, capacidad_maxima: int = None):
        self._codigo_de_paralelo = codigo_de_paralelo
        self._nombre = nombre
        self._jornada = jornada
        self._modalidad = modalidad
        self._capacidad_maxima = (
            capacidad_maxima if capacidad_maxima is not None
            else Paralelo.CAPACIDAD_MAXIMA_PREDETERMINADA
        )
        self._docente_responsable = None
        self._estudiantes_matriculados = []
        self._horarios = []

    # ── Properties (Encapsulación) ──

    @property
    def codigo_de_paralelo(self):
        return self._codigo_de_paralelo

    @codigo_de_paralelo.setter
    def codigo_de_paralelo(self, valor: str):
        self._codigo_de_paralelo = valor

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        self._nombre = valor

    @property
    def jornada(self):
        return self._jornada

    @property
    def modalidad(self):
        return self._modalidad

    @property
    def capacidad_maxima(self):
        return self._capacidad_maxima

    @capacidad_maxima.setter
    def capacidad_maxima(self, valor: int):
        self._capacidad_maxima = valor

    @property
    def docente_responsable(self):
        return self._docente_responsable

    @property
    def horarios(self):
        """Lista de horarios del paralelo (acceso público para iteración)."""
        return self._horarios

    @property
    def total_estudiantes_matriculados(self):
        """Cantidad de estudiantes actualmente matriculados."""
        return len(self._estudiantes_matriculados)

    @property
    def cupos_disponibles(self):
        """Cantidad de cupos restantes en el paralelo."""
        return self._capacidad_maxima - len(self._estudiantes_matriculados)

    # ── Validaciones de negocio ──

    def validar_datos_de_registro(self) -> dict:
        """
        Valida los campos obligatorios para el registro de un paralelo.

        Returns:
            dict con errores por campo (vacío si todo es correcto)
        """
        errores = {}

        if not self._nombre or not self._nombre.strip():
            errores["nombre"] = "Información requerida"

        if not isinstance(self._jornada, Jornada):
            errores["jornada"] = "registro no válido"

        if not isinstance(self._modalidad, Modalidad):
            errores["modalidad"] = "registro no válido"

        if not isinstance(self._capacidad_maxima, int) or self._capacidad_maxima <= 0:
            errores["capacidad_maxima"] = "el registro no puede ser negativo"

        return errores

    def tiene_cupo_disponible(self) -> bool:
        """Verifica si hay cupos disponibles para matricular estudiantes."""
        return len(self._estudiantes_matriculados) < self._capacidad_maxima

    # ── Gestión de estudiantes ──

    def vincular_estudiante(self, estudiante: Estudiante) -> bool:
        """
        Matricula un estudiante en el paralelo.

        Validaciones:
            - Debe haber cupo disponible
            - El estudiante no debe estar ya matriculado

        Returns:
            True si se vinculó correctamente, False si no cumple validaciones
        """
        if not self.tiene_cupo_disponible():
            return False

        if estudiante in self._estudiantes_matriculados:
            return False

        self._estudiantes_matriculados.append(estudiante)
        return True

    def desvincular_estudiante(self, estudiante: Estudiante) -> bool:
        """
        Retira un estudiante del paralelo.

        Returns:
            True si se desvinculó correctamente, False si no pertenecía al paralelo
        """
        if estudiante not in self._estudiantes_matriculados:
            return False

        self._estudiantes_matriculados.remove(estudiante)
        return True

    # ── Gestión de docente ──

    def vincular_docente(self, docente: Docente) -> bool:
        """
        Asigna un docente responsable al paralelo.
        Solo permite un docente a la vez.

        Returns:
            True si se vinculó correctamente, False si ya hay docente asignado
        """
        if self._docente_responsable is not None:
            return False

        self._docente_responsable = docente
        return True

    def desvincular_docente(self) -> bool:
        """
        Remueve al docente responsable del paralelo.

        Returns:
            True si se desvinculó, False si no había docente asignado
        """
        if self._docente_responsable is None:
            return False

        self._docente_responsable = None
        return True

    # ── Gestión de horarios ──

    def agregar_horario(self, horario: Horario):
        """Agrega una sesión de horario al paralelo."""
        self._horarios.append(horario)

    def calcular_horas_agendadas(self) -> float:
        """
        Calcula el total de horas agendadas sumando la duración de todos los horarios.

        Returns:
            Total de horas agendadas (redondeado a 2 decimales)
        """
        total_de_horas = 0.0
        for horario in self._horarios:
            total_de_horas += horario.determinar_duracion_horas()
        return round(total_de_horas, 2)

    def encontrar_conflicto_horario(self, nuevo_horario: Horario,
                                     horarios_externos: list = None) -> Horario:
        """
        Busca si un nuevo horario entra en conflicto con los horarios existentes
        del paralelo o con horarios externos proporcionados.

        Args:
            nuevo_horario: Horario candidato a agregar
            horarios_externos: Horarios de otros paralelos/docente a considerar

        Returns:
            El Horario en conflicto, o None si no hay conflicto
        """
        horarios_a_revisar = list(self._horarios)
        if horarios_externos:
            horarios_a_revisar.extend(horarios_externos)

        for horario in horarios_a_revisar:
            if nuevo_horario.verificar_conflicto_horario(horario):
                return horario
        return None

    def validar_nuevo_horario(self, nuevo_horario: Horario,
                              horas_sincronicas_requeridas: float,
                              horarios_externos: list = None) -> dict:
        """
        Validación completa para agregar un nuevo horario al paralelo.

        Verifica:
            1. Que no exista conflicto horario
            2. Que las horas agendadas no excedan las horas sincrónicas requeridas

        Args:
            nuevo_horario: Horario candidato
            horas_sincronicas_requeridas: Límite de horas semanales de la unidad
            horarios_externos: Horarios de otros paralelos/docente

        Returns:
            {"ok": True} si es válido
            {"ok": False, "motivo": "conflicto", "horario_en_conflicto": Horario}
            {"ok": False, "motivo": "horas", "horas_actuales": float, "horas_nuevas": float}
        """
        conflicto = self.encontrar_conflicto_horario(nuevo_horario, horarios_externos)
        if conflicto is not None:
            return {
                "ok": False,
                "motivo": "conflicto",
                "horario_en_conflicto": conflicto,
            }

        horas_actuales = self.calcular_horas_agendadas()
        horas_nuevas = nuevo_horario.determinar_duracion_horas()
        if horas_actuales + horas_nuevas > horas_sincronicas_requeridas:
            return {
                "ok": False,
                "motivo": "horas",
                "horas_actuales": horas_actuales,
                "horas_nuevas": horas_nuevas,
            }

        return {"ok": True, "motivo": ""}

    # ── Comportamiento de dominio ──

    @staticmethod
    def generar_nombre_por_indice(indice: int) -> str:
        """
        Genera el nombre de un paralelo basado en un índice secuencial.

        Nomenclatura:
            0 → "Paralelo A", 1 → "Paralelo B", ..., 25 → "Paralelo Z"
            26 → "Paralelo A1", 27 → "Paralelo B1", ...

        Args:
            indice: Índice base-0 del paralelo

        Returns:
            Nombre generado (ej: "Paralelo A", "Paralelo C1")
        """
        letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if indice < 26:
            return f"Paralelo {letras[indice]}"
        ciclo = (indice - 26) // 26 + 1
        pos = (indice - 26) % 26
        return f"Paralelo {letras[pos]}{ciclo}"
