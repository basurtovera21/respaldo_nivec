# 1. Importaciones de Django
from django import forms

# 2. Importaciones de tus Modelos (Base de datos)
from .models import (
    UsuarioDeSistema, 
    PerfilDocente, 
    PerfilEstudiante, 
    PerfilAdministrativo
)

# 3. Importaciones de tu Capa Lógica (POO) - Clases Base
from poo.clases.usuarios.usuario_administrativo import UsuarioAdministrativo as UsuarioAdministrativoBase

# 4. Importaciones de tu Capa Lógica (POO) - Enums
from poo.clases.enums.estado_de_usuario import EstadoDeUsuario
from poo.clases.enums import perfil_administrativo


class FormularioUsuarioDeSistema(forms.ModelForm):
    contrasena = forms.CharField(
        label="Contraseña predefinida",
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': True,
            'placeholder': 'Número de identificación registrado',
            'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;'
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_de_identificacion'].required = False
        self.fields['identificacion'].required = False
        self.fields['nombres'].required = False
        self.fields['apellidos'].required = False
        self.fields['correo_institucional'].required = False
        self.fields['estado_de_usuario'].required = False

    def clean(self):
        cleaned_data = super().clean()
        tipo_id = cleaned_data.get("tipo_de_identificacion")
        identificacion = cleaned_data.get("identificacion")
        nombres = cleaned_data.get("nombres")
        apellidos = cleaned_data.get("apellidos")
        correo = cleaned_data.get("correo_institucional")
        estado = cleaned_data.get("estado_de_usuario")

        errores = {}

        if not tipo_id:
            errores['tipo_de_identificacion'] = "Información requerida"
        if not identificacion:
            errores['identificacion'] = "Información requerida"
        if not nombres:
            errores['nombres'] = "Información requerida"
        if not apellidos:
            errores['apellidos'] = "Información requerida"
        if not correo:
            errores['correo_institucional'] = "Información requerida"
        if not estado:
            errores['estado_de_usuario'] = "Información requerida"

        if identificacion and 'identificacion' not in errores:
            try:
                UsuarioAdministrativoBase.validar_creacion_de_usuario_administrativo(
                    identificacion=identificacion, 
                    contrasena=identificacion 
                )
            except ValueError as e:
                errores['identificacion'] = str(e)

        if errores:
            raise forms.ValidationError(errores)

        return cleaned_data


class FormularioModificarUsuarioDeSistema(forms.ModelForm):
    contrasena = forms.CharField(
        label="Nueva contraseña", 
        widget=forms.PasswordInput(attrs={'class': 'campo-input'}), 
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apagamos la validación HTML5 para todos los campos al modificar
        for field in self.fields.values():
            field.required = False

    def clean(self):
        datos_limpios = super().clean()
        
        # Validar campos requeridos manualmente
        campos_requeridos = ["tipo_de_identificacion", "identificacion", "nombres", "apellidos", "correo_institucional", "estado_de_usuario"]
        errores = {}
        
        for campo in campos_requeridos:
            if not datos_limpios.get(campo):
                errores[campo] = "Información requerida"

        contrasena = datos_limpios.get("contrasena")
        confirmar_contrasena = datos_limpios.get("confirmar_contrasena")
        identificacion = datos_limpios.get("identificacion") or self.instance.identificacion

        if contrasena or confirmar_contrasena:
            if contrasena != confirmar_contrasena:
                errores['contrasena'] = "Las contraseñas registradas no coinciden."
            else:
                try:
                    UsuarioAdministrativoBase.validar_creacion_de_usuario_administrativo(
                        identificacion=identificacion, 
                        contrasena=contrasena
                    )
                except ValueError as e:
                    errores['contrasena'] = str(e)
                    
        if errores:
            raise forms.ValidationError(errores)
                
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


from django import forms
from .models import PerfilEstudiante

class FormularioPerfilEstudiante(forms.ModelForm): # Nombre corregido para evitar el ImportError
    class Meta:
        model = PerfilEstudiante
        fields = (
            "identificador_institucional", 
            "numero_de_matricula", 
            "jornada", 
            "registro_de_cupo", 
            "carrera_registrada", 
            "campus_registrado", 
            "estado_de_matricula"
        )
        labels = {
            "identificador_institucional": "Número de identificador institucional",
            "numero_de_matricula": "Número de matrícula",
            "jornada": "Jornada registrada",
            "registro_de_cupo": "Registro de cupo",
            "carrera_registrada": "Carrera registrada",
            "campus_registrado": "Campus registrado",
            "estado_de_matricula": "Estado de matrícula"
        }
        widgets = {
            "identificador_institucional": forms.TextInput(attrs={
                'placeholder': 'El identificador será determinado de forma automática',
                'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
                'readonly': True
            }),
            "numero_de_matricula": forms.TextInput(attrs={
                'placeholder': 'El número de matrícula será determinado de forma automática',
                'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
                'readonly': True
            }),
            "jornada": forms.Select(attrs={'class': 'campo-select'}),
            "registro_de_cupo": forms.Select(attrs={'class': 'campo-select'}),
            "carrera_registrada": forms.Select(attrs={'class': 'campo-select'}),
            "campus_registrado": forms.Select(attrs={'class': 'campo-select'}),
            "estado_de_matricula": forms.Select(attrs={'class': 'campo-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Los campos autogenerados no deben requerir entrada del usuario
        self.fields['identificador_institucional'].required = False
        self.fields['numero_de_matricula'].required = False


class FormularioPerfilAdministrativo(forms.ModelForm):
    # CORRECCIÓN AQUÍ: Usar 'perfil_administrativo.PerfilAdministrativo' en lugar del nombre no definido
    CHOICES_ALL = [(e.value, e.value) for e in perfil_administrativo.PerfilAdministrativo]
    
    perfil_administrativo = forms.ChoiceField(
        choices=CHOICES_ALL,
        label="Perfil administrativo",
        widget=forms.Select(attrs={'class': 'campo-select'})
    )

    class Meta:
        model = PerfilAdministrativo
        fields = ("identificador_administrativo", "perfil_administrativo")
        labels = {
            "identificador_administrativo": "Número de identificador administrativo", 
            "perfil_administrativo": "Perfil administrativo"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'perfil_administrativo' in self.fields:
            self.fields['perfil_administrativo'].required = False
        
        # ESCUDO PARA LA HERENCIA: Solo aplica si la clase tiene este campo
        if 'identificador_administrativo' in self.fields:
            self.fields['identificador_administrativo'].required = False
            self.fields['identificador_administrativo'].widget.attrs.update({
                'placeholder': 'El identificador será determinado de forma automática',
                'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
                'readonly': True
            })

    def clean(self):
        cleaned_data = super().clean()
        perfil = cleaned_data.get("perfil_administrativo")

        errores = {}

        if not perfil:
            errores['perfil_administrativo'] = "Información requerida"

        if errores:
            raise forms.ValidationError(errores)

        return cleaned_data


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
        
class FormularioRegistrarCoordinadorDAN(FormularioPerfilAdministrativo):
    class Meta(FormularioPerfilAdministrativo.Meta):
        # Usamos el campo específico del DAN en vez del genérico
        fields = ("identificador_coordinador_dan", "perfil_administrativo")
        labels = {
            "identificador_coordinador_dan": "Número de identificador DAN", 
            "perfil_administrativo": "Perfil administrativo"
        }
        widgets = {
            "identificador_coordinador_dan": forms.TextInput(attrs={
                'placeholder': 'El identificador será determinado de forma automática',
                'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
                'readonly': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['perfil_administrativo'].choices = [
            (perfil_administrativo.PerfilAdministrativo.COORDINADOR_DAN.value, 'Coordinador de dirección de admisión y nivelación'),
        ]
        self.fields['perfil_administrativo'].widget.attrs.update({
            'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
            'readonly': True
        })
        self.fields['identificador_coordinador_dan'].required = False


class FormularioModificarCoordinadorDAN(forms.ModelForm):
    class Meta:
        model = PerfilAdministrativo
        fields = ("identificador_coordinador_dan",)
        labels = {"identificador_coordinador_dan": "Número de identificador DAN"}
        widgets = {
            "identificador_coordinador_dan": forms.TextInput(attrs={
                'readonly': True,
                'style': 'background-color: #f5f5f7; color: #86868b; cursor: not-allowed;'
            }),
        }
        
class FormularioRegistrarCoordinadorUA(FormularioPerfilAdministrativo):
    class Meta(FormularioPerfilAdministrativo.Meta):
        # Usamos los campos específicos del UA
        fields = ("identificador_coordinador_ua", "unidad_academica", "perfil_administrativo")
        labels = {
            "identificador_coordinador_ua": "Número de identificador UA", 
            "unidad_academica": "Unidad académica",
            "perfil_administrativo": "Perfil administrativo"
        }
        widgets = {
            "identificador_coordinador_ua": forms.TextInput(attrs={
                'placeholder': 'El identificador será determinado de forma automática',
                'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
                'readonly': True
            }),
            "unidad_academica": forms.TextInput(attrs={'class': 'campo-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asignar el rol por defecto
        self.fields['perfil_administrativo'].choices = [
            (perfil_administrativo.PerfilAdministrativo.COORDINADOR_UA.value, 'Coordinador de unidad académica'),
        ]
        self.fields['perfil_administrativo'].widget.attrs.update({
            'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
            'readonly': True
        })
        
        # Desactivamos validación HTML5 para los campos nuevos
        if 'identificador_coordinador_ua' in self.fields:
            self.fields['identificador_coordinador_ua'].required = False
        if 'unidad_academica' in self.fields:
            self.fields['unidad_academica'].required = False

    def clean(self):
        # El super().clean() validará 'perfil_administrativo' gracias al padre
        cleaned_data = super().clean()
        unidad_academica = cleaned_data.get("unidad_academica")

        errores = {}
        if not unidad_academica:
            errores['unidad_academica'] = "Información requerida"

        if errores:
            raise forms.ValidationError(errores)

        return cleaned_data


# === FORMULARIO PARA LA PARTE DOCENTE (HERENCIA MÚLTIPLE) ===
class FormularioDatosDocenteUA(forms.ModelForm):
    class Meta:
        model = PerfilDocente
        fields = ("tipo_de_vinculacion", "tiempo_de_dedicacion", "carga_horaria_maxima")
        labels = {
            "tipo_de_vinculacion": "Tipo de vinculación",
            "tiempo_de_dedicacion": "Tiempo de dedicación",
            "carga_horaria_maxima": "Carga horaria máxima (horas)",
        }
        widgets = {
            "tipo_de_vinculacion": forms.Select(attrs={'class': 'campo-select'}),
            "tiempo_de_dedicacion": forms.Select(attrs={'class': 'campo-select'}),
            "carga_horaria_maxima": forms.NumberInput(attrs={'class': 'campo-input', 'step': '0.1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apagamos validación HTML5
        for field in self.fields:
            self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        tipo_vinculacion = cleaned_data.get("tipo_de_vinculacion")
        tiempo_dedicacion = cleaned_data.get("tiempo_de_dedicacion")
        carga_horaria = cleaned_data.get("carga_horaria_maxima")

        errores = {}
        if not tipo_vinculacion:
            errores['tipo_de_vinculacion'] = "Información requerida"
        if not tiempo_dedicacion:
            errores['tiempo_de_dedicacion'] = "Información requerida"
        if carga_horaria is None:
            errores['carga_horaria_maxima'] = "Información requerida"
            
        if errores:
            raise forms.ValidationError(errores)
            
        return cleaned_data


# === FORMULARIO PARA MODIFICAR ===
class FormularioModificarCoordinadorUA(forms.ModelForm):
    class Meta:
        model = PerfilAdministrativo
        fields = ("identificador_coordinador_ua", "unidad_academica")
        labels = {
            "identificador_coordinador_ua": "Número de identificador UA",
            "unidad_academica": "Unidad académica"
        }
        widgets = {
            "identificador_coordinador_ua": forms.TextInput(attrs={
                'readonly': True,
                'style': 'background-color: #f5f5f7; color: #86868b; cursor: not-allowed;'
            }),
            "unidad_academica": forms.TextInput(attrs={'class': 'campo-input'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unidad_academica'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("unidad_academica"):
            self.add_error('unidad_academica', "Información requerida")
        return cleaned_data
    
    
class FormularioRegistrarDocente(forms.ModelForm):
    especialidades_texto = forms.CharField(
        label="Especialidades",
        required=False,
        widget=forms.TextInput(attrs={'class': 'campo-input'}),
        help_text="Registre la infromacioón separadas por comas"
    )

    class Meta:
        model = PerfilDocente
        fields = ("identificador_institucional", "tipo_de_vinculacion", "tiempo_de_dedicacion", "carga_horaria_maxima")
        labels = {
            "identificador_institucional": "Número de identificador institucional",
            "tipo_de_vinculacion": "Tipo de vinculación",
            "tiempo_de_dedicacion": "Tiempo de dedicación",
            "carga_horaria_maxima": "Carga horaria máxima (horas)"
        }
        widgets = {
            "identificador_institucional": forms.TextInput(attrs={
                'placeholder': 'El identificador será determinado de forma automática',
                'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
                'readonly': True
            }),
            "tipo_de_vinculacion": forms.Select(attrs={'class': 'campo-select'}),
            "tiempo_de_dedicacion": forms.Select(attrs={'class': 'campo-select'}),
            "carga_horaria_maxima": forms.NumberInput(attrs={'class': 'campo-input', 'step': '0.1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['identificador_institucional'].required = False
        
        # Si estamos modificando, pre-llenar el campo de texto con la lista unida por comas
        if self.instance and self.instance.pk and self.instance.especialidades:
            self.fields['especialidades_texto'].initial = ", ".join(self.instance.especialidades)

    def clean(self):
        cleaned_data = super().clean()
        
        # Validación de campos
        errores = {}
        if not cleaned_data.get("tipo_de_vinculacion"): errores['tipo_de_vinculacion'] = "Información requerida"
        if not cleaned_data.get("tiempo_de_dedicacion"): errores['tiempo_de_dedicacion'] = "Información requerida"
        if cleaned_data.get("carga_horaria_maxima") is None: errores['carga_horaria_maxima'] = "Información requerida"
        
        if errores: raise forms.ValidationError(errores)

        # Convertir el texto a lista para el JSONField
        texto_esp = cleaned_data.get("especialidades_texto", "")
        if texto_esp:
            # Separa por comas, limpia espacios vacíos a los lados de cada palabra
            cleaned_data['especialidades'] = [esp.strip() for esp in texto_esp.split(',') if esp.strip()]
        else:
            cleaned_data['especialidades'] = []
            
        return cleaned_data