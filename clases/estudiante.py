from usuario_academico import UsuarioAcademico


class Estudiante(UsuarioAcademico):
    def __init__(self, tipo_de_identificacion, identificacion, nombres, apellidos, correo, contrasena, fecha_de_nacimiento, sexo, etnia, porcentaje_de_discapacidad, celular, direccion, estado, codigo_academico, codigo_carrera, estado_matricula, **kwargs):
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
        self.codigo_carrera = codigo_carrera
        self.estado_matricula = estado_matricula
     
     
     
    def formalizar_matricula(self):
        pass
    def obtener_carrera(self):
        pass
    def obtener_registro_de_unidades_curriculares(self):
        pass
    def solicitar_retiro(self):
        pass