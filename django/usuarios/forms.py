from django import forms
from .models import UsuarioDeSistema, PerfilDocente, PerfilEstudiante, PerfilAdministrativo
from poo.clases.enums.estado_de_usuario import EstadoDeUsuario
from poo.clases.enums import perfil_administrativo

class FormularioUsuarioDeSistema(forms.ModelForm):
    contrasena = forms.CharField(
        label="Contraseña predefinida",
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': True,
            'placeholder': 'Número de identificación registrado',
            'style': 'background-color: #f5f5f7; color: #86868b; cursor: not-allowed;'
        })
    )
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
        fields = ("tipo_de_identificacion", "identificacion", "nombres", "apellidos", "correo_institucional", "estado_de_usuario")
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
        }

class FormularioModificarUsuarioDeSistema(forms.ModelForm):
    contrasena = forms.CharField(
        label="Nueva contraseña", 
        widget=forms.PasswordInput(attrs={'class': 'campo-input'}), 
        min_length=8, 
        required=False,
        help_text="No realice cambios en este campo si no desea cambiar la contraseña"
    )
    confirmar_contrasena = forms.CharField(
        label="Confirmar nueva contraseña", 
        widget=forms.PasswordInput(attrs={'class': 'campo-input'}), 
        required=False
    )
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
        fields = ("tipo_de_identificacion", "identificacion", "nombres", "apellidos", "correo_institucional", "fecha_de_nacimiento", "sexo", "etnia", "porcentaje_de_discapacidad", "celular", "direccion", "estado_de_usuario")
        labels = {
            "tipo_de_identificacion": "Tipo de identificación", "identificacion": "Número de identificación", "nombres": "Nombres", "apellidos": "Apellidos", "correo_institucional": "Correo institucional", "fecha_de_nacimiento": "Fecha de nacimiento", "sexo": "Sexo", "etnia": "Etnia", "porcentaje_de_discapacidad": "Porcentaje de discapacidad", "celular": "Número de celular", "direccion": "Dirección domiciliaria", "estado_de_usuario": "Estado de usuario",
        }
        widgets = {
            "tipo_de_identificacion": forms.Select(attrs={'class': 'campo-select'}),
            "fecha_de_nacimiento": forms.DateInput(attrs={'type': 'date', 'class': 'campo-input'}),
            "sexo": forms.TextInput(attrs={'class': 'campo-input'}),
        }

    def clean(self):
        datos_limpios = super().clean()
        contrasena = datos_limpios.get("contrasena")
        confirmar_contrasena = datos_limpios.get("confirmar_contrasena")
        if contrasena or confirmar_contrasena:
            if contrasena != confirmar_contrasena:
                raise forms.ValidationError("Las contraseñas registradas no coinciden.")
        return datos_limpios


class FormularioPerfilDocente(forms.ModelForm):
    class Meta:
        model = PerfilDocente
        fields = ("usuario_de_sistema", "identificador_institucional", "tipo_de_vinculacion", "tiempo_de_dedicacion", "estado_de_vinculacion", "carga_horaria_maxima", "carga_horaria_actual", "especialidades")
        widgets = {
            "identificador_institucional": forms.TextInput(attrs={'readonly': True}),
            "carga_horaria_actual": forms.NumberInput(attrs={'readonly': True}),
            "tipo_de_vinculacion": forms.Select(attrs={'class': 'campo-select'}),
            "tiempo_de_dedicacion": forms.Select(attrs={'class': 'campo-select'}),
            "estado_de_vinculacion": forms.Select(attrs={'class': 'campo-select'}),
        }


class FormularioPerfilEstudiante(forms.ModelForm):
    class Meta:
        model = PerfilEstudiante
        fields = ("usuario_de_sistema", "identificador_institucional", "numero_de_matricula", "jornada", "registro_de_cupo", "carrera_registrada", "campus_registrado", "estado_de_matricula")
        widgets = {
            "identificador_institucional": forms.TextInput(attrs={'readonly': True}),
            "numero_de_matricula": forms.TextInput(attrs={'readonly': True}),
            "jornada": forms.Select(attrs={'class': 'campo-select'}),
            "registro_de_cupo": forms.Select(attrs={'class': 'campo-select'}),
            "carrera_registrada": forms.Select(attrs={'class': 'campo-select'}),
            "campus_registrado": forms.Select(attrs={'class': 'campo-select'}),
            "estado_de_matricula": forms.Select(attrs={'class': 'campo-select'}),
        }


class FormularioPerfilAdministrativo(forms.ModelForm):
    CHOICES_ALL = [(e.value, e.value) for e in perfil_administrativo.PerfilAdministrativo]
    
    perfil_administrativo = forms.ChoiceField(
        choices=CHOICES_ALL,
        label="Perfil administrativo",
        widget=forms.Select(attrs={'class': 'campo-select'})
    )

    class Meta:
        model = PerfilAdministrativo
        fields = ("identificador_administrativo", "perfil_administrativo")
        labels = {"identificador_administrativo": "Número de identificador administrativo", "perfil_administrativo": "Perfil administrativo"}
        widgets = {
            "identificador_administrativo": forms.TextInput(attrs={
                'readonly': True,
                'placeholder': 'El identificador será determinado de forma automática',
                'style': 'background-color: #f5f5f7; color: #86868b; cursor: not-allowed;'
            }),
        }


class FormularioRegistrarPerfilAdministrativo(FormularioPerfilAdministrativo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['perfil_administrativo'].choices = [
            (perfil_administrativo.PerfilAdministrativo.RECTOR.value, 'Rector'),
            (perfil_administrativo.PerfilAdministrativo.VICERRECTOR_ACADEMICO.value, 'Vicerrector académico'),
        ]


class FormularioModificarPerfilAdministrativo(forms.ModelForm):
    class Meta:
        model = PerfilAdministrativo
        fields = ("identificador_administrativo",)
        labels = {"identificador_administrativo": "Número de identificador administrativo"}
        widgets = {
            "identificador_administrativo": forms.TextInput(attrs={
                'readonly': True,
                'style': 'background-color: #f5f5f7; color: #86868b; cursor: not-allowed;'
            }),
        }