from django import forms
from .models import (UsuarioDeSistema, PerfilDocente, PerfilEstudiante, PerfilAdministrativo)
from poo.clases.enums.estado_de_usuario import EstadoDeUsuario

class FormularioUsuarioDeSistema(forms.ModelForm):
    contrasena = forms.CharField(label="Contraseña", widget=forms.PasswordInput, min_length=8, required=True)
    confirmar_contrasena = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput, required=True)

    estado_de_usuario = forms.ChoiceField(
        choices=[
            (EstadoDeUsuario.ACTIVO.value, 'Activo'),
            (EstadoDeUsuario.INACTIVO.value, 'Inactivo'),
            (EstadoDeUsuario.BLOQUEADO.value, 'Bloqueado'),
        ],
        label="Estado de usuario",
        widget=forms.Select(attrs={'class': 'campo-select'})
    )

    class Meta:
        model = UsuarioDeSistema
        fields = (
            "tipo_de_identificacion", "identificacion", "nombres", "apellidos", 
            "correo_institucional", "estado_de_usuario"
        )
        labels = {
            "tipo_de_identificacion": "Tipo de identificación",
            "identificacion": "Número de identificación",
            "nombres": "Nombres",
            "apellidos": "Apellidos",
            "correo_institucional": "Correo institucional",
            "estado_de_usuario": "Estado de usuario",
        }
        widgets = {
            "tipo_de_identificacion": forms.Select(attrs={'class': 'campo-select'}),
            "estado_de_usuario": forms.Select(attrs={'class': 'campo-select'}),
        }

    def clean(self):
        registro_valido = super().clean()
        contrasena = registro_valido.get("contrasena")
        confirmar_contrasena = registro_valido.get("confirmar_contrasena")
        if contrasena and confirmar_contrasena and contrasena != confirmar_contrasena:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return registro_valido


class FormularioPerfilDocente(forms.ModelForm):
    class Meta:
        model = PerfilDocente
        fields = (
            "usuario_de_sistema", "identificador_institucional", "tipo_de_vinculacion", 
            "tiempo_de_dedicacion", "estado_de_vinculacion", "carga_horaria_maxima", 
            "carga_horaria_actual", "especialidades"
        )
        labels = {
            "usuario_de_sistema": "Usuario de sistema registrado",
            "identificador_institucional": "Número de identificador institucional",
            "tipo_de_vinculacion": "Tipo de vinculación",
            "tiempo_de_dedicacion": "Tiempo de dedicación",
            "estado_de_vinculacion": "Estado de vinculación",
            "carga_horaria_maxima": "Carga horaria máxima (en horas)",
            "carga_horaria_actual": "Carga horaria actual (en horas)",
            "especialidades": "Especialidades",
        }
        widgets = {
            "carga_horaria_actual": forms.NumberInput(attrs={'readonly': True}),
            "tipo_de_vinculacion": forms.Select(attrs={'class': 'campo-select'}),
            "tiempo_de_dedicacion": forms.Select(attrs={'class': 'campo-select'}),
            "estado_de_vinculacion": forms.Select(attrs={'class': 'campo-select'}),
        }
        help_texts = {
            "especialidades": "Ingrese las especialidades separadas por comas."
        }


class FormularioPerfilEstudiante(forms.ModelForm):
    class Meta:
        model = PerfilEstudiante
        fields = (
            "usuario_de_sistema", "identificador_institucional", "numero_de_matricula", 
            "jornada", "registro_de_cupo", "carrera_registrada", "campus_registrado", 
            "estado_de_matricula"
        )
        labels = {
            "usuario_de_sistema": "Usuario de sistema registrado",
            "identificador_institucional": "Número de identificador institucional",
            "numero_de_matricula": "Número de matrícula",
            "jornada": "Jornada registrada",
            "registro_de_cupo": "Registro de cupo",
            "carrera_registrada": "Carrera registrada",
            "campus_registrado": "Campus registrado",
            "estado_de_matricula": "Estado de matrícula",
        }
        widgets = {
            "jornada": forms.Select(attrs={'class': 'campo-select'}),
            "registro_de_cupo": forms.Select(attrs={'class': 'campo-select'}),
            "carrera_registrada": forms.Select(attrs={'class': 'campo-select'}),
            "campus_registrado": forms.Select(attrs={'class': 'campo-select'}),
            "estado_de_matricula": forms.Select(attrs={'class': 'campo-select'}),
        }


class FormularioPerfilAdministrativo(forms.ModelForm):
    OPCIONES_PERFIL_ADMINISTRATIVO = [
        ('Rector', 'Rector'),
        ('Vicerrector académico', 'Vicerrector académico'),
    ]

    perfil_administrativo = forms.ChoiceField(
        choices=OPCIONES_PERFIL_ADMINISTRATIVO,
        label="Perfil administrativo",
        widget=forms.Select(attrs={'class': 'campo-select'})
    )

    class Meta:
        model = PerfilAdministrativo
        fields = (
            "identificador_administrativo", 
            "perfil_administrativo"
        )
        labels = {
            "identificador_administrativo": "Número de identificador administrativo",
            "perfil_administrativo": "Perfil administrativo"
        }