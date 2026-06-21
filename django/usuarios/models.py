from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin

#poo/
from poo.clases.enums.tipo_de_identificacion import TipoDeIdentificacion
from poo.clases.enums.estado_de_usuario import EstadoDeUsuario
from poo.clases.enums.tipo_de_vinculacion import TipoDeVinculacion
from poo.clases.enums.tiempo_de_dedicacion import TiempoDeDedicacion
from poo.clases.enums.estado_de_vinculacion import EstadoDeVinculacion
from poo.clases.enums.jornada import Jornada
from poo.clases.enums.registro_de_cupo import RegistroDeCupo
from poo.clases.enums.estado_de_matricula import EstadoDeMatricula
from poo.clases.enums.perfil_administrativo import PerfilAdministrativo


def cambiar_enum_a_choices(enum_clase):
    lista_de_opciones = []
    for opcion in enum_clase:
        tupla_opcion = (opcion.value, opcion.value) #Tupla de dos elementos (valor en base de datos, valor en sistema)
        lista_de_opciones.append(tupla_opcion)
        
    return lista_de_opciones


class CreadorDeUsuarios(BaseUserManager):
    def create_user(self, correo_institucional, password=None, **kwargs):
        if not correo_institucional:
            raise ValueError("No se ha proporcionado un correo institucional.")
        
        correo_institucional = self.normalize_email(correo_institucional)
        usuario_de_sistema = self.model(correo_institucional=correo_institucional, **kwargs)
        usuario_de_sistema.set_password(password)
        usuario_de_sistema.save(using=self._db)
        return usuario_de_sistema

    def create_superuser(self, correo_institucional, password=None, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        return self.create_user(correo_institucional, password, **kwargs)


class UsuarioDeSistema(AbstractBaseUser, PermissionsMixin):
    tipo_de_identificacion = models.CharField(max_length=50, choices=cambiar_enum_a_choices(TipoDeIdentificacion), verbose_name="Tipo de identificación")
    identificacion = models.CharField(max_length=20, unique=True, verbose_name="Número de identificación")
    nombres = models.CharField(max_length=150, verbose_name="Nombres")
    apellidos = models.CharField(max_length=150, verbose_name="Apellidos")
    correo_institucional = models.EmailField(unique=True, verbose_name="Correo institucional")
    
    fecha_de_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    sexo = models.CharField(max_length=20, null=True, blank=True, verbose_name="Sexo")
    etnia = models.CharField(max_length=50, null=True, blank=True, verbose_name="Etnia")
    porcentaje_de_discapacidad = models.FloatField(default=0.0, null=True, blank=True, verbose_name="Porcentaje de discapacidad")
    celular = models.CharField(max_length=15, null=True, blank=True, verbose_name="Número de celular")
    direccion = models.CharField(max_length=300, null=True, blank=True, verbose_name="Dirección")
    
    estado_de_usuario = models.CharField(max_length=50, choices=cambiar_enum_a_choices(EstadoDeUsuario), default=EstadoDeUsuario.PENDIENTE.value, verbose_name="Estado de usuario")
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CreadorDeUsuarios()

    USERNAME_FIELD = "correo_institucional"
    REQUIRED_FIELDS = ["identificacion", "nombres", "apellidos"]

    class Meta:
        verbose_name = "Usuario del sistema"
        verbose_name_plural = "Usuarios del sistema"

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.correo_institucional})"


class PerfilDocente(models.Model):
    usuario_de_sistema = models.OneToOneField(UsuarioDeSistema, on_delete=models.CASCADE, related_name="perfil_docente", verbose_name="Usuario de sistema registrado")
    identificador_institucional = models.CharField(max_length=50, unique=True, verbose_name="Número de identificador institucional")
    tipo_de_vinculacion = models.CharField(max_length=50, choices=cambiar_enum_a_choices(TipoDeVinculacion), verbose_name="Tipo de vinculación")
    tiempo_de_dedicacion = models.CharField(max_length=50, choices=cambiar_enum_a_choices(TiempoDeDedicacion), verbose_name="Tiempo de dedicación")
    estado_de_vinculacion = models.CharField(max_length=50, choices=cambiar_enum_a_choices(EstadoDeVinculacion), default=EstadoDeVinculacion.ACTIVO.value, verbose_name="Estado de vinculación")
    carga_horaria_maxima = models.FloatField(default=40.0, verbose_name="Carga horaria máxima (en horas)")
    carga_horaria_actual = models.FloatField(default=0.0, verbose_name="Carga horaria actual (en horas)")
    especialidades = models.JSONField(default=list, verbose_name="Especialidades") #Lista

    class Meta:
        verbose_name = "Perfil docente"
        verbose_name_plural = "Perfiles docentes"

    def __str__(self):
        return f"DOCENTE: {self.usuario_de_sistema.nombres} {self.usuario_de_sistema.apellidos}"


class PerfilEstudiante(models.Model):
    usuario_de_sistema = models.OneToOneField(
        UsuarioDeSistema, 
        on_delete=models.CASCADE, 
        related_name="perfil_estudiante", 
        verbose_name="Usuario de sistema registrado"
    )
    identificador_institucional = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Número de identificador institucional"
    )
    numero_de_matricula = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Número de matrícula"
    )
    jornada = models.CharField(
        max_length=50, 
        choices=cambiar_enum_a_choices(Jornada), 
        verbose_name="Jornada registrada"
    )
    registro_de_cupo = models.CharField(
        max_length=50, 
        choices=cambiar_enum_a_choices(RegistroDeCupo), 
        verbose_name="Registro de cupo"
    )
    
    carrera_registrada = models.ForeignKey(
        'academico.Carrera', 
        on_delete=models.PROTECT, 
        related_name="estudiantes"
    )
    campus_registrado = models.ForeignKey(
        'academico.Campus', 
        on_delete=models.PROTECT, 
        related_name="estudiantes"
    )
    
    # ACTUALIZADO: Default ahora es MATRICULADO
    estado_de_matricula = models.CharField(
        max_length=50, 
        choices=cambiar_enum_a_choices(EstadoDeMatricula), 
        default=EstadoDeMatricula.MATRICULADO.value, 
        verbose_name="Estado de matrícula"
    )
    
    class Meta:
        verbose_name = "Perfil estudiante"
        verbose_name_plural = "Perfiles estudiantes"

    def __str__(self):
        return f"ESTUDIANTE: {self.usuario_de_sistema.nombres} {self.usuario_de_sistema.apellidos}"


class PerfilAdministrativo(models.Model):
    usuario_de_sistema = models.OneToOneField(UsuarioDeSistema, on_delete=models.CASCADE, related_name="perfil_administrativo", verbose_name="Usuario de sistema registrado")
    universidad = models.ForeignKey('academico.Universidad', on_delete=models.SET_NULL, related_name="administrativos", verbose_name="Universidad registrada", null=True, blank=True)
    identificador_administrativo = models.CharField(max_length=50, unique=True, verbose_name="Número de identificador administrativo")
    perfil_administrativo = models.CharField(max_length=100, choices=cambiar_enum_a_choices(PerfilAdministrativo), verbose_name="Perfil administrativo")
    identificador_coordinador_dan = models.CharField(max_length=50, null=True, blank=True, unique=True, verbose_name="Número de identificador DAN")
    identificador_coordinador_ua = models.CharField(max_length=50, null=True, blank=True, unique=True, verbose_name="Número de identificador UA")
    unidad_academica = models.CharField(max_length=200, null=True, blank=True, verbose_name="Unidad académica")
    
    class Meta:
        verbose_name = "Perfil administrativo"
        verbose_name_plural = "Perfiles administrativos"

    def __str__(self):
        return f"{self.perfil_administrativo.upper()}: {self.usuario_de_sistema.nombres} {self.usuario_de_sistema.apellidos}"