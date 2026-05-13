from usuario_de_sistema import UsuarioDeSistema


class UsuarioAdministrativo(UsuarioDeSistema):
    def __init__(self, tipo_de_identificacion, identificacion, nombres, apellidos, correo, contrasena, fecha_de_nacimiento, sexo, etnia, porcentaje_de_discapacidad, celular, direccion, estado, codigo_administrativo, **kwargs):
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
        self.codigo_administrativo = codigo_administrativo
        
        
    def crear_periodo_academico(self):
        pass
    def crear_unidad_curricular(self):
        pass
    def crear_malla_curricular(self):
        pass
    def distribuir_carga_académica(self):
        pass