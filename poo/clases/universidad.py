import unicodedata


class Universidad:
    """
    Entidad que representa una institución de educación superior registrada en el sistema.

    Responsabilidades:
        - Encapsular los datos institucionales
        - Validar la integridad de los datos de registro
        - Verificar unicidad del código SNIESE
        - Proveer resumen de información institucional

    Principios:
        - SRP: Solo gestiona datos y validaciones de la universidad
        - Encapsulación: Atributos protegidos con acceso controlado vía properties
    """

    _LONGITUD_MAXIMA_ABREVIATURA = 20

    def __init__(self, nombre: str, abreviatura: str, codigo_sniese: str, direccion_matriz: str = ""):
        self._nombre = nombre
        self._abreviatura = abreviatura
        self._codigo_sniese = codigo_sniese
        self._direccion_matriz = direccion_matriz

    # ── Properties (Encapsulación) ──

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        self._nombre = valor

    @property
    def abreviatura(self):
        return self._abreviatura

    @abreviatura.setter
    def abreviatura(self, valor: str):
        self._abreviatura = valor

    @property
    def codigo_sniese(self):
        return self._codigo_sniese

    @property
    def direccion_matriz(self):
        return self._direccion_matriz

    @direccion_matriz.setter
    def direccion_matriz(self, valor: str):
        self._direccion_matriz = valor

    # ── Validaciones de negocio ──

    def validar_datos_de_registro(self) -> dict:
        """
        Valida los campos obligatorios para el registro de una universidad.
        Retorna un diccionario de errores (vacío si todo es correcto).
        """
        errores = {}

        if not self._nombre or not str(self._nombre).strip():
            errores["nombre"] = "Información requerida"

        if not self._abreviatura or not str(self._abreviatura).strip():
            errores["abreviatura"] = "Información requerida"
        elif len(str(self._abreviatura).strip()) > self._LONGITUD_MAXIMA_ABREVIATURA:
            errores["abreviatura"] = f"La abreviatura no debe exceder {self._LONGITUD_MAXIMA_ABREVIATURA} caracteres"

        if not self._codigo_sniese or not str(self._codigo_sniese).strip():
            errores["codigo_sniese"] = "Información requerida"

        return errores

    def validar_codigo_sniese_unico(self, codigos_existentes: set) -> bool:
        """
        Verifica que el código SNIESE de esta universidad no exista
        en el conjunto proporcionado (normalizado para comparación).
        """
        codigo_normalizado = Universidad.normalizar_texto(self._codigo_sniese)
        return codigo_normalizado not in codigos_existentes

    # ── Comportamiento de dominio ──

    def recuperar_informacion_institucional(self) -> dict:
        """
        Retorna un resumen estructurado de los datos institucionales.
        Útil para reportes, informes y visualización.
        """
        return {
            "Nombre": self._nombre,
            "Abreviatura": self._abreviatura,
            "Código SNIESE": self._codigo_sniese,
            "Dirección de matriz": self._direccion_matriz,
        }

    # ── Utilidades ──

    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """
        Normaliza un texto para comparaciones insensibles a mayúsculas,
        espacios y acentos.
        """
        if not texto:
            return ""
        texto = str(texto).strip().lower()
        texto = ''.join(
            caracter for caracter in unicodedata.normalize('NFD', texto)
            if unicodedata.category(caracter) != 'Mn'
        )
        return texto

    def __str__(self):
        return f"{self._nombre} ({self._abreviatura})"
