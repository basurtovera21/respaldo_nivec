from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout

from poo.clases.usuarios.estudiante import Estudiante as EstudianteBase
from poo.clases.usuarios.docente import Docente as DocenteBase
from poo.clases.enums.estado_de_matricula import EstadoDeMatricula
from poo.clases.enums.estado_de_vinculacion import EstadoDeVinculacion

from poo.clases.enums.jornada import Jornada
from poo.clases.enums.registro_de_cupo import RegistroDeCupo
from poo.clases.enums.tipo_de_vinculacion import TipoDeVinculacion
from poo.clases.enums.tiempo_de_dedicacion import TiempoDeDedicacion
from poo.clases.enums.tipo_de_identificacion import TipoDeIdentificacion
from .models import PerfilEstudiante, PerfilDocente, PerfilAdministrativo

#UsuarioDeSistema
def servicio_iniciar_sesion(request, correo_institucional, contrasena):
    usuario_de_sistema = authenticate(request, username=correo_institucional, password=contrasena)
    if usuario_de_sistema is not None:
        login(request, usuario_de_sistema)
        return True
    
    return False


def servicio_cerrar_sesion(request):
    logout(request)


#Estudiante
def servicio_formalizar_matricula(perfil_estudiante: PerfilEstudiante):
    estudiante = _construir_estudiante(perfil_estudiante)
    formalizar_matricula = estudiante.formalizar_matricula()
    if formalizar_matricula:
        perfil_estudiante.estado_de_matricula = EstadoDeMatricula.MATRICULADO.value
        perfil_estudiante.save()
    return formalizar_matricula


def servicio_anular_matricula(perfil_estudiante: PerfilEstudiante):
    estudiante = _construir_estudiante(perfil_estudiante)
    anular_matricula = estudiante.anular_matricula()
    if anular_matricula:
        perfil_estudiante.estado_de_matricula = EstadoDeMatricula.ANULADO.value
        perfil_estudiante.save()
    return anular_matricula
    
    

def servicio_solicitar_retiro(perfil_estudiante: PerfilEstudiante):
    estudiante = _construir_estudiante(perfil_estudiante)
    solicitar_retiro = estudiante.solicitar_retiro()
    if solicitar_retiro:
        perfil_estudiante.estado_de_matricula = EstadoDeMatricula.RETIRADO.value
        perfil_estudiante.save()
    return solicitar_retiro


def servicio_aprobar_retiro(perfil_estudiante: PerfilEstudiante):
    estudiante = _construir_estudiante(perfil_estudiante)
    aprobar_retiro = estudiante.aprobar_retiro()
    if aprobar_retiro:
        perfil_estudiante.estado_de_matricula = EstadoDeMatricula.RETIRADO.value
        perfil_estudiante.save()
    return aprobar_retiro


#Docente
def servicio_visualizar_carga_academica(perfil_docente: PerfilDocente):
    docente = _construir_docente(perfil_docente)
    return docente.visualizar_carga_academica()


def servicio_inhabilitar_perfil_docente(perfil_docente: PerfilDocente):
    docente = _construir_docente(perfil_docente)
    docente.inhabilitar_perfil()
    perfil_docente.estado_de_vinculacion = EstadoDeVinculacion.INACTIVO.value
    perfil_docente.save()

#UsuarioAcademico
def servicio_obtener_registro_institucional(perfil_estudiante: PerfilEstudiante):
    estudiante = _construir_estudiante(perfil_estudiante)
    return estudiante.obtener_registro_institucional()


#Constructores
def _construir_estudiante(perfil_estudiante: PerfilEstudiante):
    from poo.clases.carrera import Carrera as CarreraBase
    from poo.clases.campus import Campus as CampusBase
    from poo.clases.enums.modalidad import Modalidad

    carrera = CarreraBase(
        codigo_de_carrera = perfil_estudiante.carrera_registrada.codigo_de_carrera,
        nombre = perfil_estudiante.carrera_registrada.nombre,
        modalidad = Modalidad(perfil_estudiante.carrera_registrada.modalidad),
        campo_de_conocimiento = perfil_estudiante.carrera_registrada.campo_de_conocimiento,
        vigencia_sniese = perfil_estudiante.carrera_registrada.vigencia_sniese
    )
    
    campus = CampusBase(
        codigo_de_campus = perfil_estudiante.campus_registrado.codigo_de_campus,
        nombre = perfil_estudiante.campus_registrado.nombre,
        direccion_fisica = perfil_estudiante.campus_registrado.direccion_fisica,
        provincia = perfil_estudiante.campus_registrado.provincia,
        infraestructura_compartida = perfil_estudiante.campus_registrado.infraestructura_compartida
    )
    
    usuario_de_sistema = perfil_estudiante.usuario_de_sistema
    return EstudianteBase(
        tipo_de_identificacion = TipoDeIdentificacion(usuario_de_sistema.tipo_de_identificacion),
        identificacion = usuario_de_sistema.identificacion,
        nombres = usuario_de_sistema.nombres,
        apellidos = usuario_de_sistema.apellidos,
        correo_institucional = usuario_de_sistema.correo_institucional,
        contrasena = "temporal",
        fecha_de_nacimiento = usuario_de_sistema.fecha_de_nacimiento,
        sexo = usuario_de_sistema.sexo,
        etnia = usuario_de_sistema.etnia,
        porcentaje_de_discapacidad = usuario_de_sistema.porcentaje_de_discapacidad,
        celular = usuario_de_sistema.celular,
        direccion = usuario_de_sistema.direccion,
        identificador_institucional = perfil_estudiante.identificador_institucional,
        numero_de_matricula = perfil_estudiante.numero_de_matricula,
        jornada = Jornada(perfil_estudiante.jornada),
        registro_de_cupo = RegistroDeCupo(perfil_estudiante.registro_de_cupo),
        carrera_registrada = carrera,
        campus_registrado = campus,
        estado_de_matricula = EstadoDeMatricula(perfil_estudiante.estado_de_matricula)
    )


def _construir_docente(perfil_docente: PerfilDocente):
    usuario_de_sistema = perfil_docente.usuario_de_sistema
    docente = DocenteBase(
        tipo_de_identificacion = TipoDeIdentificacion(usuario_de_sistema.tipo_de_identificacion),
        identificacion = usuario_de_sistema.identificacion,
        nombres = usuario_de_sistema.nombres,
        apellidos = usuario_de_sistema.apellidos,
        correo_institucional = usuario_de_sistema.correo_institucional,
        contrasena = "temporal",
        fecha_de_nacimiento = usuario_de_sistema.fecha_de_nacimiento,
        sexo = usuario_de_sistema.sexo,
        etnia = usuario_de_sistema.etnia,
        porcentaje_de_discapacidad = usuario_de_sistema.porcentaje_de_discapacidad,
        celular = usuario_de_sistema.celular,
        direccion = usuario_de_sistema.direccion,
        identificador_institucional = perfil_docente.identificador_institucional,
        tipo_de_vinculacion = TipoDeVinculacion(perfil_docente.tipo_de_vinculacion),
        tiempo_de_dedicacion = TiempoDeDedicacion(perfil_docente.tiempo_de_dedicacion),
        carga_horaria_maxima = perfil_docente.carga_horaria_maxima
    )
    docente._carga_horaria_actual = perfil_docente.carga_horaria_actual
    docente._especialidades = perfil_docente.especialidades
    docente._estado_de_vinculacion = EstadoDeVinculacion(perfil_docente.estado_de_vinculacion)
    return docente


def _construir_administrativo(perfil_administrativo: PerfilAdministrativo):
    from poo.clases.usuarios.usuario_administrativo import UsuarioAdministrativo as UsuarioAdministrativoBase
    from poo.clases.enums.perfil_administrativo import PerfilAdministrativo as PerfilAdministrativo

    usuario_de_sistema = perfil_administrativo.usuario_de_sistema
    return UsuarioAdministrativoBase(
        tipo_de_identificacion=TipoDeIdentificacion(usuario_de_sistema.tipo_de_identificacion),
        identificacion=usuario_de_sistema.identificacion,
        nombres=usuario_de_sistema.nombres,
        apellidos=usuario_de_sistema.apellidos,
        correo_institucional=usuario_de_sistema.correo_institucional,
        contrasena="temporal",
        fecha_de_nacimiento=usuario_de_sistema.fecha_de_nacimiento,
        sexo=usuario_de_sistema.sexo,
        etnia=usuario_de_sistema.etnia,
        porcentaje_de_discapacidad=usuario_de_sistema.porcentaje_de_discapacidad,
        celular=usuario_de_sistema.celular,
        direccion=usuario_de_sistema.direccion,
        identificador_administrativo=perfil_administrativo.identificador_administrativo,
        perfil_administrativo=PerfilAdministrativo(perfil_administrativo.perfil_administrativo) 
    )