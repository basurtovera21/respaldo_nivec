from usuario_administrativo import UsuarioAdministrativo
from docente import Docente


class CoordinadorAcademico(UsuarioAdministrativo, Docente):
    def __init__(self, tipo_de_identificacion, identificacion, nombres, apellidos, correo, contrasena, fecha_de_nacimiento, sexo, etnia, porcentaje_de_discapacidad, celular, direccion, estado, codigo_administrativo, codigo_academico, tipo_de_vinculacion, tiempo_dedicacion, codigo_coordinador, **kwargs):
        super().__init__(
            tipo_de_identificacion = tipo_de_identificacion,
            identificacion = identificacion,
            nombres = nombres,
            apellidos = apellidos,
            correo = correo,
            contrasena = contrasena,
            fecha_de_nacimiento = fecha_de_nacimiento,
            sexo = sexo,
            etnia = etnia,
            porcentaje_de_discapacidad = porcentaje_de_discapacidad,
            celular = celular,
            direccion = direccion,
            estado = estado,
            codigo_administrativo = codigo_administrativo,
            codigo_academico = codigo_academico,
            tipo_de_vinculacion = tipo_de_vinculacion,
            tiempo_dedicacion = tiempo_dedicacion,
            **kwargs
            )
        self.codigo_coordinador = codigo_coordinador
        
        
    def definir_espacio_de_imparticion(self):
        pass
    def registrar_docente(self):
        pass
    def actualizar_datos_docente(self):
        pass
    def inhabilitar_docente(self):
        pass
    def registrar_consolidado_de_estudiante(self):
        pass
    def conformar_cohorte_de_matricula(self):
        pass
    def crear_paralelo(self):
        pass
    def supervisar_horarios(self):
        pass
    def aprobar_retiro_estudiante(self):
        pass
    def anular_matricula_estudiante(self):
        pass
    def consolidar_resultados_nivelacion(self):
        pass