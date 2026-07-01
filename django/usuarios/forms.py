from django import forms
from academico.models import Campus, Carrera, PeriodoDeNivelacion
from .models import UsuarioDeSistema, PerfilDocente, PerfilEstudiante, PerfilAdministrativo
from poo.clases.usuarios.usuario_de_sistema import UsuarioDeSistema as UsuarioDeSistemaBase
from poo.clases.enums.estado_de_usuario import EstadoDeUsuario
from poo.clases.enums import perfil_administrativo
from poo.clases.enums.jornada import Jornada


# Solo se permiten jornadas continuas: una sola, o Matutina-Vespertina, o Vespertina-Nocturna.
_JORNADAS_ORDENADAS = [Jornada.MATUTINA.value, Jornada.VESPERTINA.value, Jornada.NOCTURNA.value]

def validar_jornadas_continuas(jornadas):
    if not jornadas:
        return "Información requerida"
    if any(j not in _JORNADAS_ORDENADAS for j in jornadas):
        return "Jornada no válida"
    if len(jornadas) > 2:
        return "La especificación de la Jornada no es continua"
    indices = sorted(_JORNADAS_ORDENADAS.index(j) for j in jornadas)
    if len(indices) == 2 and indices[1] - indices[0] != 1:
        return "La especificación de la Jornada no es continua"
    return None

class FormularioUsuarioDeSistema(forms.ModelForm):
    contrasena = forms.CharField(label="Contraseña predefinida", required=False, widget=forms.TextInput(attrs={'readonly': True, 'placeholder': 'Número de identificación registrado', 'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;'}))
    estado_de_usuario = forms.ChoiceField(choices=[(EstadoDeUsuario.ACTIVO.value, 'Activo'), (EstadoDeUsuario.INACTIVO.value, 'Inactivo'), (EstadoDeUsuario.BLOQUEADO.value, 'Bloqueado')], label="Estado de usuario", widget=forms.Select(attrs={'class': 'campo-select'}))
    
    class Meta:
        model = UsuarioDeSistema
        fields = ("tipo_de_identificacion", "identificacion", "nombres", "apellidos", "correo_institucional", "estado_de_usuario")
        labels = {"tipo_de_identificacion": "Tipo de identificación", "identificacion": "Número de identificación", "nombres": "Nombres", "apellidos": "Apellidos", "correo_institucional": "Correo institucional", "estado_de_usuario": "Estado de usuario"}
        widgets = {"tipo_de_identificacion": forms.Select(attrs={'class': 'campo-select'})}
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.error_messages.update({'required': ''}); field.required = False
        
    def clean(self):
        cleaned_data = super().clean()
        errores = {field: "Información requerida" for field in ["tipo_de_identificacion", "identificacion", "nombres", "apellidos", "correo_institucional", "estado_de_usuario"] if not cleaned_data.get(field)}
        
        if cleaned_data.get("identificacion") and "identificacion" not in errores:
            try: 
                UsuarioDeSistemaBase.validar_contrasena(cleaned_data["identificacion"])
            except ValueError as e: 
                errores['identificacion'] = str(e)
                
        if errores: raise forms.ValidationError(errores)
        return cleaned_data

class FormularioModificarUsuarioDeSistema(forms.ModelForm):
    contrasena = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput(attrs={'class': 'campo-input'}), required=False, help_text="No realice cambios en este campo si no desea cambiar la contraseña")
    confirmar_contrasena = forms.CharField(label="Confirmar nueva contraseña", widget=forms.PasswordInput(attrs={'class': 'campo-input'}), required=False)
    estado_de_usuario = forms.ChoiceField(choices=[(EstadoDeUsuario.ACTIVO.value, 'Activo'), (EstadoDeUsuario.INACTIVO.value, 'Inactivo'), (EstadoDeUsuario.BLOQUEADO.value, 'Bloqueado')], label="Estado de usuario", widget=forms.Select(attrs={'class': 'campo-select'}))
    
    class Meta:
        model = UsuarioDeSistema
        fields = ("tipo_de_identificacion", "identificacion", "nombres", "apellidos", "correo_institucional", "fecha_de_nacimiento", "sexo", "etnia", "porcentaje_de_discapacidad", "celular", "direccion", "estado_de_usuario")
        labels = {"tipo_de_identificacion": "Tipo de identificación", "identificacion": "Número de identificación", "nombres": "Nombres", "apellidos": "Apellidos", "correo_institucional": "Correo institucional", "fecha_de_nacimiento": "Fecha de nacimiento", "sexo": "Sexo", "etnia": "Etnia", "porcentaje_de_discapacidad": "Porcentaje de discapacidad", "celular": "Número de celular", "direccion": "Dirección domiciliaria", "estado_de_usuario": "Estado de usuario"}
        widgets = {"tipo_de_identificacion": forms.Select(attrs={'class': 'campo-select'}), "fecha_de_nacimiento": forms.DateInput(attrs={'type': 'date', 'class': 'campo-input'}), "sexo": forms.TextInput(attrs={'class': 'campo-input'})}
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.error_messages.update({'required': ''}); field.required = False
        
    def clean(self):
        cleaned_data = super().clean()
    
        campos_requeridos = ["tipo_de_identificacion", "identificacion", "nombres", "apellidos", "correo_institucional", "estado_de_usuario"]

        errores = {
            field: "Información requerida" 
            for field in campos_requeridos 
            if field in self.fields and not cleaned_data.get(field)
        }
        
        contrasena, confirmar = cleaned_data.get("contrasena"), cleaned_data.get("confirmar_contrasena")
        
        if contrasena or confirmar:
            try: 
                UsuarioDeSistemaBase.validar_contrasena(contrasena, confirmar)
            except ValueError as e: 
                errores['contrasena'] = str(e)
                
        if errores: raise forms.ValidationError(errores)
        return cleaned_data

class FormularioPerfilEstudiante(forms.ModelForm):
    class Meta:
        model = PerfilEstudiante
        fields = ("identificador_institucional", "numero_de_matricula", "jornada", 
                  "registro_de_cupo", "carrera_registrada", "estado_de_matricula")
        widgets = {
            "identificador_institucional": forms.TextInput(attrs={'readonly': True, 'placeholder': 'El identificador será definido de forma automática', 'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;'}), 
            "numero_de_matricula": forms.TextInput(attrs={'readonly': True, 'placeholder': 'El número de matrícula será definido de forma automática', 'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;'}), 
            "jornada": forms.Select(attrs={'class': 'campo-select'}), 
            "registro_de_cupo": forms.Select(attrs={'class': 'campo-select'}), 
            "carrera_registrada": forms.Select(attrs={'class': 'campo-select'}),
            "estado_de_matricula": forms.Select(attrs={'class': 'campo-select'})
        }

    def __init__(self, *args, **kwargs):
        universidad = kwargs.pop('universidad', None)
        
        super().__init__(*args, **kwargs)

        if universidad:
            self.fields['carrera_registrada'].queryset = Carrera.objects.filter(campus__universidad=universidad)

        for field in self.fields.values():
            field.error_messages.update({'required': ''})
        self.fields['identificador_institucional'].required = False
        self.fields['numero_de_matricula'].required = False


class FormularioRegistrarDocente(forms.ModelForm):
    especialidades_texto = forms.CharField(label="Especialidades", required=False, widget=forms.TextInput(attrs={'class': 'campo-input'}), help_text="Registre la información separada por comas")
    jornadas = forms.MultipleChoiceField(label="Jornada", required=False, choices=[(j.value, j.value) for j in Jornada], widget=forms.CheckboxSelectMultiple, help_text="Registre jornadas continuas (de ser necesario)")
    class Meta:
        model = PerfilDocente
        fields = ("identificador_institucional", "tipo_de_vinculacion", "tiempo_de_dedicacion", "carga_horaria_maxima")
        widgets = {
            "identificador_institucional": forms.TextInput(attrs={'readonly': True, 'placeholder': 'El identificador será definido de forma automática', 'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;'}), 
            "tipo_de_vinculacion": forms.Select(attrs={'class': 'campo-select'}), 
            "tiempo_de_dedicacion": forms.Select(attrs={'class': 'campo-select'}), 
            "carga_horaria_maxima": forms.NumberInput(attrs={'class': 'campo-input', 'step': '0.1'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.error_messages.update({'required': ''})
        self.fields['identificador_institucional'].required = False
        if self.instance and self.instance.pk and self.instance.especialidades: self.fields['especialidades_texto'].initial = ", ".join(self.instance.especialidades)
        if self.instance and self.instance.pk and self.instance.jornadas: self.fields['jornadas'].initial = self.instance.jornadas
    def clean(self):
        cleaned_data = super().clean()
        errores = {field: "Información requerida" for field in ["tipo_de_vinculacion", "tiempo_de_dedicacion"] if not cleaned_data.get(field)}
        carga = cleaned_data.get("carga_horaria_maxima")
        if carga is None: errores['carga_horaria_maxima'] = "Información requerida"
        elif carga < 0: errores['carga_horaria_maxima'] = "Registro no válido"
        error_jornadas = validar_jornadas_continuas(cleaned_data.get("jornadas") or [])
        if error_jornadas: errores['jornadas'] = error_jornadas
        if errores: raise forms.ValidationError(errores)
        texto_esp = cleaned_data.get("especialidades_texto", "")
        cleaned_data['especialidades'] = [esp.strip() for esp in texto_esp.split(',') if esp.strip()] if texto_esp else []
        return cleaned_data

class FormularioDatosDocenteUA(forms.ModelForm):
    jornadas = forms.MultipleChoiceField(label="Jornada", required=False, choices=[(j.value, j.value) for j in Jornada], widget=forms.CheckboxSelectMultiple, help_text="Registre jornadas continuas (de ser necesario)")
    class Meta:
        model = PerfilDocente
        fields = ("tipo_de_vinculacion", "tiempo_de_dedicacion", "carga_horaria_maxima")
        widgets = {"tipo_de_vinculacion": forms.Select(attrs={'class': 'campo-select'}), "tiempo_de_dedicacion": forms.Select(attrs={'class': 'campo-select'}), "carga_horaria_maxima": forms.NumberInput(attrs={'class': 'campo-input', 'step': '0.1'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.error_messages.update({'required': ''}); field.required = False
        if self.instance and self.instance.pk and self.instance.jornadas: self.fields['jornadas'].initial = self.instance.jornadas
    def clean(self):
        cleaned_data = super().clean()
        errores = {field: "Información requerida" for field in ["tipo_de_vinculacion", "tiempo_de_dedicacion"] if not cleaned_data.get(field)}
        carga = cleaned_data.get("carga_horaria_maxima")
        if carga is None: errores['carga_horaria_maxima'] = "Información requerida"
        elif carga < 0: errores['carga_horaria_maxima'] = "Registro no válido"
        error_jornadas = validar_jornadas_continuas(cleaned_data.get("jornadas") or [])
        if error_jornadas: errores['jornadas'] = error_jornadas
        if errores: raise forms.ValidationError(errores)
        return cleaned_data

class FormularioPerfilAdministrativo(forms.ModelForm):
    CHOICES_ALL = [(e.value, e.value) for e in perfil_administrativo.PerfilAdministrativo]
    perfil_administrativo = forms.ChoiceField(choices=CHOICES_ALL, label="Perfil administrativo", widget=forms.Select(attrs={'class': 'campo-select'}))
    class Meta:
        model = PerfilAdministrativo
        fields = ("identificador_administrativo", "perfil_administrativo")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.error_messages.update({'required': ''})
        self.fields['perfil_administrativo'].required = False
        if 'identificador_administrativo' in self.fields:
            self.fields['identificador_administrativo'].required = False
            self.fields['identificador_administrativo'].widget.attrs.update({'readonly': True, 'placeholder': 'El identificador será definido de forma automática', 'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;'})
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("perfil_administrativo"): raise forms.ValidationError({'perfil_administrativo': "Información requerida"})
        return cleaned_data

class FormularioRegistrarPerfilAdministrativo(FormularioPerfilAdministrativo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['perfil_administrativo'].choices = [(perfil_administrativo.PerfilAdministrativo.RECTOR.value, 'Rector'), (perfil_administrativo.PerfilAdministrativo.VICERRECTOR_ACADEMICO.value, 'Vicerrector académico')]

class FormularioModificarPerfilAdministrativo(forms.ModelForm):
    class Meta:
        model = PerfilAdministrativo
        fields = ("identificador_administrativo",)
        widgets = {"identificador_administrativo": forms.TextInput(attrs={'readonly': True, 'placeholder': 'El identificador será definido de forma automática', 'style': 'background-color: #f5f5f7; color: #86868b; cursor: not-allowed;'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.error_messages.update({'required': ''})

class FormularioRegistrarCoordinadorDAN(FormularioPerfilAdministrativo):
    class Meta(FormularioPerfilAdministrativo.Meta):
        fields = ("identificador_coordinador_dan", "perfil_administrativo")
        widgets = {"identificador_coordinador_dan": forms.TextInput(attrs={'readonly': True, 'placeholder': 'El identificador será definido de forma automática', 'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['perfil_administrativo'].choices = [(perfil_administrativo.PerfilAdministrativo.COORDINADOR_DAN.value, 'Coordinador de dirección de admisión y nivelación')]
        self.fields['perfil_administrativo'].widget.attrs.update({'readonly': True, 'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;'})
        self.fields['identificador_coordinador_dan'].required = False

class FormularioModificarCoordinadorDAN(forms.ModelForm):
    class Meta:
        model = PerfilAdministrativo
        fields = ("identificador_coordinador_dan",)
        widgets = {"identificador_coordinador_dan": forms.TextInput(attrs={'readonly': True, 'placeholder': 'El identificador será definido de forma automática', 'style': 'background-color: #f5f5f7; color: #86868b; cursor: not-allowed;'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.error_messages.update({'required': ''})

class FormularioRegistrarCoordinadorUA(FormularioPerfilAdministrativo):
    class Meta(FormularioPerfilAdministrativo.Meta):
        fields = ("identificador_coordinador_ua", "unidad_academica", "perfil_administrativo")
        widgets = {"identificador_coordinador_ua": forms.TextInput(attrs={'readonly': True, 'placeholder': 'El identificador será definido de forma automática', 'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;'}), "unidad_academica": forms.TextInput(attrs={'class': 'campo-input'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.error_messages.update({'required': ''})
        self.fields['perfil_administrativo'].choices = [(perfil_administrativo.PerfilAdministrativo.COORDINADOR_UA.value, 'Coordinador de unidad académica')]
        self.fields['perfil_administrativo'].widget.attrs.update({'readonly': True, 'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;'})
        self.fields['identificador_coordinador_ua'].required = self.fields['unidad_academica'].required = False
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("unidad_academica"): raise forms.ValidationError({'unidad_academica': "Información requerida"})
        return cleaned_data

class FormularioModificarCoordinadorUA(forms.ModelForm):
    class Meta:
        model = PerfilAdministrativo
        fields = ("identificador_coordinador_ua", "unidad_academica")
        widgets = {"identificador_coordinador_ua": forms.TextInput(attrs={'readonly': True, 'placeholder': 'El identificador será definido de forma automática', 'style': 'background-color: #f5f5f7; color: #86868b; cursor: not-allowed;'}), "unidad_academica": forms.TextInput(attrs={'class': 'campo-input'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.error_messages.update({'required': ''})
        self.fields['unidad_academica'].required = False
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("unidad_academica"): self.add_error('unidad_academica', "Información requerida")
        return cleaned_data