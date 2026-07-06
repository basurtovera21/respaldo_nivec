from datetime import date

from poo.clases.usuarios.docente import Docente
from poo.clases.usuarios.usuario_administrativo import UsuarioAdministrativo


class IncidenciaAcademica:
    """
    Registra una incidencia académica asociada a un docente.

    Atributos:
        - codigo_incidencia: Identificador único
        - docente_implicado: Docente vinculado a la incidencia
        - descripcion: Detalle de la incidencia
        - fecha_incidencia: Fecha en que ocurrió
        - responsable_autorizacion: Administrativo que autoriza el registro

    Estado: Pendiente de implementación completa en Django.
    El modelo Django ya existe (academico.IncidenciaAcademica).
    """

    def __init__(self, codigo_incidencia: str, docente_implicado: Docente,
                 descripcion: str, fecha_incidencia: date,
                 responsable_autorizacion: UsuarioAdministrativo):
        self._codigo_incidencia = codigo_incidencia
        self._docente_implicado = docente_implicado
        self._descripcion = descripcion
        self._fecha_incidencia = fecha_incidencia
        self._responsable_autorizacion = responsable_autorizacion

    @property
    def codigo_incidencia(self):
        return self._codigo_incidencia

    @property
    def docente_implicado(self):
        return self._docente_implicado

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def fecha_incidencia(self):
        return self._fecha_incidencia

    @property
    def responsable_autorizacion(self):
        return self._responsable_autorizacion

    def obtener_resumen(self) -> dict:
        return {
            "Código de incidencia": self._codigo_incidencia,
            "Docente implicado": f"{self._docente_implicado.nombres} {self._docente_implicado.apellidos}",
            "Descripción": self._descripcion,
            "Fecha de incidencia": str(self._fecha_incidencia),
            "Responsable de autorización": f"{self._responsable_autorizacion.nombres} {self._responsable_autorizacion.apellidos}",
        }
