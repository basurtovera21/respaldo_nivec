import unicodedata
from datetime import date


class Carrera:
    """
    Entidad que representa una carrera universitaria vinculada a un campus.

    Responsabilidades:
        - Encapsular los datos de una carrera académica
        - Validar integridad de datos para registro individual y masivo
        - Determinar si la carrera está vigente según SNIESE
        - Detectar registros duplicados mediante normalización
        - Proveer información calculada (días de vigencia restantes)

    Principios:
        - SRP: Solo gestiona datos y reglas de negocio de la carrera
        - Encapsulación: Código inmutable post-registro, vigencia solo de lectura
    """

    def __init__(self, codigo_de_carrera: str, nombre: str, vigencia_sniese: date = None):
        self._codigo_de_carrera = codigo_de_carrera
        self._nombre = nombre
        self._vigencia_sniese = vigencia_sniese

    # ── Properties (Encapsulación) ──

    @property
    def codigo_de_carrera(self):
        return self._codigo_de_carrera

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        self._nombre = valor

    @property
    def vigencia_sniese(self):
        return self._vigencia_sniese

    # ── Validaciones de negocio ──

    def validar_datos_de_registro(self) -> dict:
        """
        Valida los campos obligatorios para el registro de una carrera.

        Returns:
            dict con errores por campo (vacío si todo es correcto)
        """
        errores = {}
        if not self._nombre or not str(self._nombre).strip():
            errores["nombre"] = "Información requerida"
        if not self._vigencia_sniese:
            errores["vigencia_sniese"] = "Información requerida"
        return errores

    def esta_activa(self) -> bool:
        """
        Determina si la carrera se encuentra vigente según la fecha SNIESE.
        Una carrera está activa si la fecha actual no ha superado su vigencia.

        Returns:
            True si la carrera está vigente, False si expiró o no tiene fecha
        """
        if not self._vigencia_sniese:
            return False
        return date.today() <= self._vigencia_sniese

    def calcular_dias_restantes_vigencia(self) -> int:
        """
        Calcula los días restantes hasta que expire la vigencia SNIESE.

        Returns:
            Número de días restantes (negativo si ya expiró, 0 si no tiene fecha)
        """
        if not self._vigencia_sniese:
            return 0
        diferencia = self._vigencia_sniese - date.today()
        return diferencia.days

    def es_registro_duplicado(self, nombres_existentes: set) -> bool:
        """
        Verifica si el nombre de esta carrera ya existe en el conjunto proporcionado.
        La comparación se realiza normalizada (sin acentos, minúsculas).

        Args:
            nombres_existentes: conjunto de nombres ya normalizados

        Returns:
            True si la carrera ya está registrada
        """
        nombre_normalizado = Carrera.normalizar_nombre(self._nombre)
        return nombre_normalizado in nombres_existentes

    # ── Comportamiento de dominio ──

    # ── Utilidades ──

    @staticmethod
    def normalizar_nombre(nombre: str) -> str:
        """
        Normaliza un nombre para comparaciones insensibles a mayúsculas,
        espacios y acentos.
        """
        if not nombre:
            return ""
        texto = str(nombre).strip().lower()
        texto = ''.join(
            caracter for caracter in unicodedata.normalize('NFD', texto)
            if unicodedata.category(caracter) != 'Mn'
        )
        return texto

    def __str__(self):
        return f"{self._nombre} ({'Vigente' if self.esta_activa() else 'Expirada'})"
