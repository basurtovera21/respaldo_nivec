from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import UsuarioDeSistema
from .models import PerfilDocente
from .models import PerfilEstudiante
from .models import PerfilAdministrativo


@admin.register(UsuarioDeSistema)
class UsuarioDeSistemaAdmin(UserAdmin):
    model = UsuarioDeSistema
    list_display = ("identificacion", "nombres", "apellidos", "correo_institucional", "estado_de_usuario", "is_staff")
    search_fields = ("identificacion", "nombres", "apellidos", "correo_institucional")
    list_filter = ("estado_de_usuario", "is_staff", "is_active")
    ordering = ("estado_de_usuario", "apellidos", "nombres")

    fieldsets = (
        (None, {
            "fields": (
                "tipo_de_identificacion", 
                "identificacion", 
                "nombres", 
                "apellidos", 
                "correo_institucional",
                "fecha_de_nacimiento", 
                "sexo", 
                "etnia", 
                "porcentaje_de_discapacidad", 
                "celular", 
                "direccion",
                "estado_de_usuario", 
                "is_active", 
                "is_staff", 
                "is_superuser", 
                "password"
            )
        }),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("identificacion", "nombres", "apellidos", "correo_institucional", "password1", "password2")
        }),
    )


@admin.register(PerfilAdministrativo)
class PerfilAdministrativoAdmin(admin.ModelAdmin):
    list_display = ("usuario_de_sistema", "perfil_administrativo", "identificador_administrativo", "universidad")
    search_fields = ("usuario_de_sistema__nombres", "usuario_de_sistema__apellidos", "identificador_administrativo", "universidad__nombre")
    list_filter = ("perfil_administrativo", "universidad")
    ordering = ("usuario_de_sistema__estado_de_usuario", "usuario_de_sistema__apellidos", "usuario_de_sistema__nombres")

    fieldsets = (
        (None, {
            "fields": (
                "usuario_de_sistema",
                "identificador_administrativo",
                "universidad",
                "perfil_administrativo",

            )
        }),
    )
    
    
@admin.register(PerfilDocente)
class PerfilDocenteAdmin(admin.ModelAdmin):
    list_display = ("usuario_de_sistema", "identificador_institucional", "tipo_de_vinculacion", "tiempo_de_dedicacion", "estado_de_vinculacion", "carga_horaria_actual", "carga_horaria_maxima")
    search_fields = ("usuario_de_sistema__nombres", "usuario_de_sistema__apellidos", "identificador_institucional")
    list_filter = ("tipo_de_vinculacion", "tiempo_de_dedicacion", "estado_de_vinculacion")
    ordering = ("usuario_de_sistema__estado_de_usuario", "usuario_de_sistema__apellidos", "usuario_de_sistema__nombres")

    fieldsets = (
        (None, {
            "fields": (
                "usuario_de_sistema", 
                "identificador_institucional", 
                "tipo_de_vinculacion",
                "estado_de_vinculacion", 
                "tiempo_de_dedicacion", 
                "carga_horaria_actual", 
                "carga_horaria_maxima"
            )
        }),
    )


@admin.register(PerfilEstudiante)
class PerfilEstudianteAdmin(admin.ModelAdmin):
    list_display = ("usuario_de_sistema", "identificador_institucional", "numero_de_matricula", "carrera_registrada", "campus_registrado", "jornada", "estado_de_matricula")
    search_fields = ("usuario_de_sistema__nombres", "usuario_de_sistema__apellidos", "numero_de_matricula", "identificador_institucional")
    list_filter = ("jornada", "carrera_registrada", "campus_registrado", "estado_de_matricula")
    ordering = ("usuario_de_sistema__estado_de_usuario", "usuario_de_sistema__apellidos", "usuario_de_sistema__nombres")

    fieldsets = (
        (None, {
            "fields": (
                "usuario_de_sistema", 
                "identificador_institucional",
                "numero_de_matricula", 
                "estado_de_matricula",
                "carrera_registrada", 
                "campus_registrado", 
                "jornada"
            )
        }),
    )