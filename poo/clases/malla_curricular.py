import copy

from poo.clases.enums.estado_de_malla import EstadoDeMalla

from poo.clases.interfaces.i_unidad_evaluable import IUnidadEvaluable
from poo.clases.interfaces.i_clonable import IClonable


class MallaCurricular(IClonable):
    """
    Entidad que representa la estructura curricular de una carrera para nivelación.

    Patrones de diseño implementados:
        - Prototype (IClonable): Permite clonar una malla completa con todas sus
          unidades curriculares, generando una nueva versión en estado de Diseño.

    Máquina de estados:
        DISEÑO → ACTIVA → HISTÓRICA
        DISEÑO → INACTIVA
        ACTIVA → INACTIVA
        (Solo una malla puede estar ACTIVA por carrera a la vez)

    Principios:
        - SRP: Gestiona estructura curricular y transiciones de estado
        - OCP: Nuevos estados se agregan sin modificar los existentes
        - ISP: Implementa IClonable (solo clonar())
        - Sobrecarga: agregar_unidad_curricular acepta una unidad o una lista

    Reglas de negocio:
        - Solo se puede editar la estructura (agregar unidades) en DISEÑO o ACTIVA
        - Solo se pueden crear paralelos con una malla ACTIVA
        - Clonar siempre produce una malla en estado DISEÑO
    """

    def __init__(self, codigo_de_malla: str, nombre: str, version_de_malla: str):
        self._codigo_de_malla = codigo_de_malla
        self._nombre = nombre
        self._version_de_malla = version_de_malla
        self._estado = EstadoDeMalla.DISENO
        self._total_horas_nivelacion = 0.0
        self._unidades_curriculares = []

    # ── Properties (Encapsulación) ──

    @property
    def codigo_de_malla(self):
        return self._codigo_de_malla

    @codigo_de_malla.setter
    def codigo_de_malla(self, valor: str):
        self._codigo_de_malla = valor

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        self._nombre = valor

    @property
    def version_de_malla(self):
        return self._version_de_malla

    @version_de_malla.setter
    def version_de_malla(self, valor: str):
        self._version_de_malla = valor

    @property
    def estado(self):
        return self._estado

    @property
    def total_horas_nivelacion(self):
        return self._total_horas_nivelacion

    # ── Máquina de estados ──

    def establecer_estado(self, estado: EstadoDeMalla) -> bool:
        """
        Establece el estado de la malla directamente (usado al reconstruir desde BD).

        Args:
            estado: Instancia de EstadoDeMalla

        Returns:
            True si se estableció correctamente
        """
        if isinstance(estado, EstadoDeMalla):
            self._estado = estado
            return True
        return False

    def puede_editar_estructura(self) -> bool:
        """Indica si se pueden agregar/modificar unidades curriculares."""
        return self._estado in (EstadoDeMalla.DISENO, EstadoDeMalla.ACTIVA)

    def esta_activa(self) -> bool:
        """Indica si la malla está en estado ACTIVA."""
        return self._estado == EstadoDeMalla.ACTIVA

    def puede_usarse_en_paralelos(self) -> bool:
        """Indica si la malla puede asociarse a paralelos (solo si está ACTIVA)."""
        return self._estado == EstadoDeMalla.ACTIVA

    def activar(self) -> bool:
        """
        Transición: DISEÑO/INACTIVA → ACTIVA.
        
        Returns:
            True si la transición fue válida
        """
        if self._estado in (EstadoDeMalla.DISENO, EstadoDeMalla.INACTIVA):
            self._estado = EstadoDeMalla.ACTIVA
            return True
        return False

    def marcar_historica(self) -> bool:
        """
        Transición: ACTIVA → HISTÓRICA.
        Se usa cuando se activa una nueva versión de la malla.

        Returns:
            True si la transición fue válida
        """
        if self._estado == EstadoDeMalla.ACTIVA:
            self._estado = EstadoDeMalla.HISTORICA
            return True
        return False

    def inactivar(self) -> bool:
        """
        Transición: DISEÑO/ACTIVA → INACTIVA.
        Deshabilita la malla sin eliminarla.

        Returns:
            True si la transición fue válida
        """
        if self._estado in (EstadoDeMalla.DISENO, EstadoDeMalla.ACTIVA):
            self._estado = EstadoDeMalla.INACTIVA
            return True
        return False

    # ── Validaciones de negocio ──

    def validar_datos_de_registro(self) -> dict:
        """
        Valida los campos obligatorios para el registro de una malla curricular.

        Returns:
            dict con errores por campo (vacío si todo es correcto)
        """
        errores = {}

        if not self._nombre or not self._nombre.strip():
            errores["nombre"] = "Información requerida"

        return errores

    # ── Patrón Prototype ──

    def clonar(self, nuevo_codigo_de_malla: str, nueva_version_de_malla: str) -> 'MallaCurricular':
        """
        Crea una copia profunda de esta malla con un nuevo código y versión.
        La malla clonada siempre comienza en estado DISEÑO.

        Patrón Prototype: Permite crear nuevas versiones de una malla
        preservando toda su estructura de unidades curriculares.

        Args:
            nuevo_codigo_de_malla: Código único para la nueva malla
            nueva_version_de_malla: Identificador de versión (ej: "V2")

        Returns:
            Nueva instancia de MallaCurricular con las unidades copiadas
        """
        malla_curricular_clonada = copy.deepcopy(self)
        malla_curricular_clonada._codigo_de_malla = nuevo_codigo_de_malla
        malla_curricular_clonada._version_de_malla = nueva_version_de_malla
        malla_curricular_clonada._estado = EstadoDeMalla.DISENO
        malla_curricular_clonada._total_horas_nivelacion = (
            malla_curricular_clonada.calcular_total_horas_nivelacion()
        )
        return malla_curricular_clonada

    # ── Gestión de unidades curriculares (Sobrecarga) ──

    def obtener_unidades_curriculares(self) -> list:
        """Retorna una copia de la lista de unidades curriculares."""
        return list(self._unidades_curriculares)

    def agregar_unidad_curricular(self, *args) -> bool:
        """
        Agrega unidades curriculares a la malla (Sobrecarga).

        Formas de invocación:
            1. agregar_unidad_curricular(unidad)         → Una sola unidad
            2. agregar_unidad_curricular([uc1, uc2])     → Lista de unidades
            3. agregar_unidad_curricular(uc1, uc2)       → Múltiples argumentos

        Validaciones:
            - Solo permite agregar si la malla está en DISEÑO o ACTIVA
            - Verifica que la unidad implemente IUnidadEvaluable
            - No permite duplicados (verifica por código de unidad)

        Returns:
            True si todas las unidades se agregaron, False si alguna falló
        """
        unidad_agregada = True
        for entrada in args:
            if isinstance(entrada, list):
                for unidad in entrada:
                    if not self._agregar_una_unidad_curricular(unidad):
                        unidad_agregada = False
            else:
                if not self._agregar_una_unidad_curricular(entrada):
                    unidad_agregada = False

        return unidad_agregada

    def _agregar_una_unidad_curricular(self, unidad_curricular: IUnidadEvaluable) -> bool:
        """
        Agrega una única unidad curricular validando reglas de negocio.

        Args:
            unidad_curricular: Debe implementar IUnidadEvaluable

        Returns:
            True si se agregó correctamente
        """
        if not self.puede_editar_estructura():
            return False

        if not isinstance(unidad_curricular, IUnidadEvaluable):
            return False

        # Verificar duplicado por código
        for unidad in self._unidades_curriculares:
            if unidad.obtener_codigo_de_unidad() == unidad_curricular.obtener_codigo_de_unidad():
                return False

        self._unidades_curriculares.append(unidad_curricular)
        self._total_horas_nivelacion = self.calcular_total_horas_nivelacion()
        return True

    # ── Cálculos de dominio ──

    def calcular_total_horas_nivelacion(self) -> float:
        """Suma total de horas (sincrónicas + asincrónicas) de todas las unidades."""
        total = 0.0
        for unidad in self._unidades_curriculares:
            total += unidad.obtener_horas_totales()
        return total

    # ── Comportamiento de dominio ──

    def __str__(self):
        return f"{self._codigo_de_malla} ({self._nombre} - {self._version_de_malla})"
