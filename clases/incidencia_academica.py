from datetime import date

#Usuarios
from clases.usuarios.docente import Docente
from clases.usuarios.usuario_administrativo import UsuarioAdministrativo


class IncidenciaAcademica:
    def __init__(self, codigo_incidencia: str, docente_implicado: Docente, descripcion: str, fecha_incidencia: date, responsable_autorizacion: UsuarioAdministrativo):
        self.codigo_incidencia = codigo_incidencia
        self.docente_implicado = docente_implicado # Instancia
        self.descripcion = descripcion
        self.fecha_incidencia = fecha_incidencia
        self.responsable_autorizacion = responsable_autorizacion #Instancia


    def obtener_resumen(self):
        return {
            "Código de incidencia": self.codigo_incidencia,
            "Docente implicado": f"{self.docente_implicado.nombres} {self.docente_implicado.apellidos}",
            "Descripcion": self.descripcion,
            "Fecha de incidencia": str(self.fecha_incidencia),
            "Responsable de autorización": f"{self.responsable_autorizacion.nombres} {self.responsable_autorizacion.apellidos} ({self.responsable_autorizacion.perfil_administrativo.value})"
        }