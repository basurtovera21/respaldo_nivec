from usuario_de_sistema import UsuarioDeSistema


class UsuarioAcademico(UsuarioDeSistema):
    def __init__(self, tipo_de_identificacion, identificacion, nombres, apellidos, correo, contrasena, fecha_de_nacimiento, sexo, etnia, porcentaje_de_discapacidad, celular, direccion, estado, codigo_academico, **kwargs):
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
            **kwargs
        )
        self.codigo_academico = codigo_academico
        
        
    def visualizar_horario(self):
        pass
    def visualizar_unidades_curriculares(self):
        pass
    def visualizar_paralelo(self):
        pass
    