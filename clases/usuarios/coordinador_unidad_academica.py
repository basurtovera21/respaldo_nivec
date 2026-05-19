#Herencia múltiple
from clases.usuarios.usuario_administrativo import UsuarioAdministrativo
from clases.usuarios.docente import Docente


class CoordinadorUnidadAcademica(UsuarioAdministrativo, Docente):
    def __init__(self, tipo_de_identificacion, identificacion: str, nombres: str, apellidos: str, correo_institucional: str, contrasena: str, fecha_de_nacimiento, sexo: str, etnia: str, porcentaje_de_discapacidad: float, celular: str, direccion: str, identificador_administrativo: str, perfil_administrativo, identificador_institucional: str, tipo_de_vinculacion, tiempo_de_dedicacion, carga_horaria_maxima: float, identificador_coordinador_ua: str, unidad_academica: str, **kwargs):
    #**kwargs; __init__ recibe solo los argumentos que le corresponden sin errores.
        super().__init__(
            tipo_de_identificacion = tipo_de_identificacion,
            identificacion = identificacion,
            nombres = nombres,
            apellidos = apellidos,
            correo_institucional = correo_institucional,
            contrasena = contrasena,
            fecha_de_nacimiento = fecha_de_nacimiento,
            sexo = sexo,
            etnia = etnia,
            porcentaje_de_discapacidad = porcentaje_de_discapacidad,
            celular = celular,
            direccion = direccion,
            identificador_administrativo = identificador_administrativo,
            perfil_administrativo = perfil_administrativo,
            identificador_institucional = identificador_institucional,
            tipo_de_vinculacion = tipo_de_vinculacion,
            tiempo_de_dedicacion = tiempo_de_dedicacion,
            carga_horaria_maxima = carga_horaria_maxima,
            **kwargs
            )
        self.identificador_coordinador_ua = identificador_coordinador_ua
        self.unidad_academica = unidad_academica
        
        
    def iniciar_sesion(self):
        print(f"[Coordinador UA] Sesión iniciada: {self.nombres} {self.apellidos} (Unidad: {self.unidad_academica})")
        
    def establecer_paralelo(self):
        pass   
     
    def definir_espacio_de_imparticion(self): #Definir entorno
        pass
    
    def supervisar_horarios(self): #Validar cronograma
        pass
    
    def registrar_docente(self):
        pass
    
    def actualizar_datos_de_docente(self):
        pass
    
    def inhabilitar_docente(self):
        pass
    
    def aprobar_retiro_estudiante(self):
        pass
    
    def anular_matricula_estudiante(self):
        pass
    
    def validar_resultados_facultad(self):
        pass
    
    def cerrar_consolidacion_facultad(self):
        pass