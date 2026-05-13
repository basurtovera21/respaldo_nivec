from usuario_academico import UsuarioAcademico


class Docente(UsuarioAcademico):
    def __init__(self, tipo_de_identificacion, identificacion, nombres, apellidos, correo, contrasena, fecha_de_nacimiento, sexo, etnia, porcentaje_de_discapacidad, celular, direccion, estado, codigo_academico, tipo_de_vinculacion, tiempo_dedicacion, **kwargs):
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
            codigo_academico = codigo_academico,
            **kwargs
        )
        self.tipo_de_vinculacion = tipo_de_vinculacion
        self.tiempo_dedicacion = tiempo_dedicacion
        
        
    def procesar_calificaciones(self):
        pass
    def procesar_asistencia_de_estudiante(self):
        pass