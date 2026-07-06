import unicodedata


class Campus:
    """
    Entidad que representa una sede o extensión física de una universidad.

    Responsabilidades:
        - Encapsular los datos de un campus universitario
        - Validar la integridad de datos para registro individual y masivo
        - Detectar registros duplicados mediante normalización de nombres
        - Proveer resumen de información del campus

    Principios:
        - SRP: Solo gestiona datos y validaciones del campus
        - Encapsulación: Código de campus inmutable, otros atributos con acceso controlado
    """

    def __init__(self, codigo_de_campus: str, nombre: str, direccion_fisica: str = "", provincia: str = ""):
        self._codigo_de_campus = codigo_de_campus
        self._nombre = nombre
        self._direccion_fisica = direccion_fisica
        self._provincia = provincia

    # ── Properties (Encapsulación) ──

    @property
    def codigo_de_campus(self):
        return self._codigo_de_campus

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        self._nombre = valor

    @property
    def direccion_fisica(self):
        return self._direccion_fisica

    @direccion_fisica.setter
    def direccion_fisica(self, valor: str):
        self._direccion_fisica = valor

    @property
    def provincia(self):
        return self._provincia

    @provincia.setter
    def provincia(self, valor: str):
        self._provincia = valor

    # ── Validaciones de negocio ──

    def validar_datos_de_registro(self) -> dict:
        """
        Valida los campos obligatorios para el registro individual de un campus.
        En registro individual la provincia es opcional.

        Returns:
            dict con errores por campo (vacío si todo es correcto)
        """
        errores = {}
        if not self._nombre or not str(self._nombre).strip():
            errores["nombre"] = "Información requerida"
        if not self._direccion_fisica or not str(self._direccion_fisica).strip():
            errores["direccion_fisica"] = "Información requerida"
        return errores

    def validar_datos_de_carga_masiva(self) -> dict:
        """
        Valida los campos obligatorios para la carga masiva desde Excel.
        En carga masiva se exige también la provincia.

        Returns:
            dict con errores por campo (vacío si todo es correcto)
        """
        errores = {}
        if not self._nombre or not str(self._nombre).strip():
            errores["nombre"] = "Información requerida"
        if not self._direccion_fisica or not str(self._direccion_fisica).strip():
            errores["direccion_fisica"] = "Información requerida"
        if not self._provincia or not str(self._provincia).strip():
            errores["provincia"] = "Información requerida"
        return errores

    def es_registro_duplicado(self, nombres_existentes: set) -> bool:
        """
        Verifica si el nombre de este campus ya existe en el conjunto proporcionado.
        La comparación se realiza normalizada (sin acentos, minúsculas).

        Args:
            nombres_existentes: conjunto de nombres ya normalizados

        Returns:
            True si el campus ya está registrado
        """
        nombre_normalizado = Campus.normalizar_nombre(self._nombre)
        return nombre_normalizado in nombres_existentes

    # ── Comportamiento de dominio ──

    def recuperar_informacion_de_campus(self) -> dict:
        """
        Retorna un resumen estructurado de los datos del campus.
        Útil para reportes, informes y visualización.
        """
        return {
            "Código de campus": self._codigo_de_campus,
            "Nombre": self._nombre,
            "Dirección física": self._direccion_fisica,
            "Provincia": self._provincia,
        }

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
        return self._nombre
