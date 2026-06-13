from django import forms
from .models import (UsuarioDeSistema, PerfilDocente, PerfilEstudiante, PerfilAdministrativo)


class FormularioUsuarioDeSistema(forms.ModelForm):
    contrasena = forms.CharField(label="Contraseña", widget=forms.PasswordInput, min_length=8)
    confirmar_contrasena = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        model = UsuarioDeSistema
        fields = (
            "tipo_de_identificacion", "identificacion", "nombres", "apellidos", 
            "correo_institucional", "fecha_de_nacimiento", "sexo", "etnia", 
            "porcentaje_de_discapacidad", "celular", "direccion", "estado_de_usuario"
        )
        labels = {
            "tipo_de_identificacion": "Tipo de identificación",
            "identificacion": "Número de identificación",
            "nombres": "Nombres",
            "apellidos": "Apellidos",
            "correo_institucional": "Correo institucional",
            "fecha_de_nacimiento": "Fecha de nacimiento",
            "sexo": "Sexo",
            "etnia": "Etnia",
            "porcentaje_de_discapacidad": "Porcentaje de discapacidad",
            "celular": "Número de celular",
            "direccion": "Dirección",
            "estado_de_usuario": "Estado de usuario",
        }
        widgets = {"fecha_de_nacimiento": forms.DateInput(attrs={"type": "date"})}

    def clean(self):
        registro_valido = super().clean()
        contrasena = registro_valido.get("contrasena")
        confirmar_contrasena = registro_valido.get("confirmar_contrasena")
        if contrasena and confirmar_contrasena and contrasena != confirmar_contrasena:
            raise forms.ValidationError("Los registros no coinciden.")
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


class FormularioPerfilAdministrativo(forms.ModelForm):
    class Meta:
        model = PerfilAdministrativo
        fields = (
            "usuario_de_sistema", "identificador_administrativo", "perfil_administrativo", 
            "identificador_coordinador_dan", "identificador_coordinador_ua", "unidad_academica",
            "universidad"
        )
        labels = {
            "usuario_de_sistema": "Usuario de sistema registrado",
            "identificador_administrativo": "Número de identificador administrativo",
            "perfil_administrativo": "Perfil administrativo",
            "identificador_coordinador_dan": "Número de identificador DAN",
            "identificador_coordinador_ua": "Número de identificador UA",
            "unidad_academica": "Unidad académica",
            "universidad": "Universidad registrada"
        }