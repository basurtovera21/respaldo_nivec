from django import forms
from .models import (Universidad, Campus, Carrera, MallaCurricular, UnidadCurricular, PeriodoDeNivelacion, Paralelo, Horario, CohorteDeMatricula, MatriculaParalelo, ConsolidadoAcademico, EvaluacionAcademica, IncidenciaAcademica, EvaluacionDeDesempeno, InformeGeneral)
from poo.clases.carrera import Carrera as CarreraBase
from poo.clases.enums.modalidad import Modalidad as EnumModalidad

class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input-estilo'})
            
            
class FormularioUniversidad(BaseModelForm):
    class Meta:
        model = Universidad
        fields = ("nombre", "abreviatura", "codigo_sniese", "direccion_matriz", "identificador_visual")
        labels = {
            "nombre": "Nombre de la institución",
            "abreviatura": "Abreviatura",
            "codigo_sniese": "Código SNIESE",
            "direccion_matriz": "Dirección de matriz",
            "identificador_visual": "Identificador visual",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.required = False

    def clean(self):
        from poo.clases.universidad import Universidad as UniversidadBase

        cleaned_data = super().clean()

        universidad_poo = UniversidadBase(
            nombre=cleaned_data.get("nombre", ""),
            abreviatura=cleaned_data.get("abreviatura", ""),
            codigo_sniese=cleaned_data.get("codigo_sniese", ""),
            direccion_matriz=cleaned_data.get("direccion_matriz", ""),
            identificador_visual=cleaned_data.get("identificador_visual"),
        )

        errores = universidad_poo.validar_datos_de_registro()
        if errores:
            raise forms.ValidationError(errores)

        codigo_sniese = (cleaned_data.get("codigo_sniese") or "").strip()
        if codigo_sniese:
            existentes = Universidad.objects.filter(codigo_sniese__iexact=codigo_sniese)
            if self.instance and self.instance.pk:
                existentes = existentes.exclude(pk=self.instance.pk)
            if existentes.exists():
                raise forms.ValidationError(
                    {"codigo_sniese": "La institución ya ha sido registrada"}
                )

        return cleaned_data




class FormularioCampus(forms.ModelForm):
    class Meta:
        model = Campus
        fields = ("codigo_de_campus", "nombre", "direccion_fisica", "provincia")
        labels = {
            "codigo_de_campus": "Código de Campus",
            "nombre": "Nombre",
            "direccion_fisica": "Dirección física",
            "provincia": "Provincia",
        }

    def __init__(self, *args, universidad=None, **kwargs):
        self.universidad = universidad
        super().__init__(*args, **kwargs)
        self.fields['nombre'].required = False
        self.fields['direccion_fisica'].required = False
        self.fields['provincia'].required = False

        self.fields['codigo_de_campus'].required = False
        self.fields['codigo_de_campus'].widget.attrs.update({
            'placeholder': 'El código será determinado de forma automática',
            'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
            'readonly': True
        })

    def clean(self):
        from poo.clases.campus import Campus as CampusBase

        cleaned_data = super().clean()

        campus_poo = CampusBase(
            codigo_de_campus=cleaned_data.get("codigo_de_campus", ""),
            nombre=cleaned_data.get("nombre", ""),
            direccion_fisica=cleaned_data.get("direccion_fisica", ""),
            provincia=cleaned_data.get("provincia", ""),
        )

        errores = campus_poo.validar_datos_de_registro()
        if errores:
            raise forms.ValidationError(errores)

        nombre = (cleaned_data.get("nombre") or "").strip()
        if nombre and self.universidad is not None:
            existentes = Campus.objects.filter(universidad=self.universidad, nombre__iexact=nombre)
            if self.instance and self.instance.pk:
                existentes = existentes.exclude(pk=self.instance.pk)
            if existentes.exists():
                raise forms.ValidationError(
                    {"El Campus ya ha sido registrado"}
                )

        return cleaned_data


class FormularioCarrera(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = ("campus", "codigo_de_carrera", "nombre", "modalidad", "facultad", "vigencia_sniese")
        labels = {
            "campus": "Campus registrado",
            "codigo_de_carrera": "Código de Carrera",
            "nombre": "Nombre",
            "modalidad": "Modalidad",
            "facultad": "Facultad",
            "vigencia_sniese": "Vigencia SNIESE",
        }
        widgets = {
            "vigencia_sniese": forms.DateInput(attrs={"type": "date"}),
            "codigo_de_carrera": forms.TextInput(attrs={
                'placeholder': 'El código será determinado de forma automática', 
                'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;', 
                'readonly': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['campus'].required = False
        self.fields['nombre'].required = False
        self.fields['modalidad'].required = False
        self.fields['facultad'].required = False
        self.fields['vigencia_sniese'].required = False
        self.fields['codigo_de_carrera'].required = False

    def clean(self):
        cleaned_data = super().clean()
        
        campus = cleaned_data.get("campus")
        nombre = cleaned_data.get("nombre")
        modalidad = cleaned_data.get("modalidad")
        facultad = cleaned_data.get("facultad")
        vigencia_sniese = cleaned_data.get("vigencia_sniese")

        errores = {}

        if not campus: errores['campus'] = "Información requerida"
        if not nombre: errores['nombre'] = "Información requerida"
        if not modalidad: errores['modalidad'] = "Información requerida"
        if not facultad: errores['facultad'] = "Información requerida"
        if not vigencia_sniese: errores['vigencia_sniese'] = "Información requerida"

        if nombre and modalidad and vigencia_sniese and facultad:
            carrera_poo = CarreraBase(
                codigo_de_carrera="PENDIENTE",
                nombre=nombre,
                modalidad=Modalidad(modalidad),
                facultad=facultad,
                vigencia_sniese=vigencia_sniese
            )

            if not carrera_poo.esta_activa():
                errores['vigencia_sniese'] = "La vigencia SNIESE ha expirado"

        if campus and nombre:
            existentes = Carrera.objects.filter(campus=campus, nombre__iexact=nombre.strip())
            if self.instance and self.instance.pk:
                existentes = existentes.exclude(pk=self.instance.pk)
            if existentes.exists():
                errores['nombre'] = "La Carrera ya ha sido registrada"

        if errores:
            raise forms.ValidationError(errores)

        return cleaned_data


class FormularioMallaCurricular(forms.ModelForm):
    class Meta:
        model = MallaCurricular
        fields = (
            "carrera",
            "codigo_de_malla",
            "nombre",
            "duracion_semanas",
        )
        labels = {
            "carrera": "Carrera registrada",
            "codigo_de_malla": "Código de Malla curricular",
            "nombre": "Nombre",
            "duracion_semanas": "Duración (en semanas)",
        }
        widgets = {
            "codigo_de_malla": forms.TextInput(attrs={
                "placeholder": "El código será determinado de forma automática",
                "style": "background-color: #f5f5f7; color: #86868b; pointer-events: none;",
                "readonly": True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        from poo.clases.malla_curricular import MallaCurricular as MallaCurricularBase

        cleaned_data = super().clean()
        errores = {}

        carrera = cleaned_data.get("carrera")
        nombre = cleaned_data.get("nombre")
        duracion = cleaned_data.get("duracion_semanas")

        if not carrera:
            errores["carrera"] = "Información requerida"

        malla_poo = MallaCurricularBase(
            codigo_de_malla="PENDIENTE",
            nombre=nombre or "",
            duracion_semanas=duracion if isinstance(duracion, int) else 0,
            version_de_malla="PENDIENTE",
        )
        errores.update(malla_poo.validar_datos_de_registro())

        if carrera and nombre and "nombre" not in errores:
            existentes = MallaCurricular.objects.filter(
                carrera=carrera, nombre__iexact=nombre.strip()
            )
            if self.instance and self.instance.pk:
                existentes = existentes.exclude(pk=self.instance.pk)
            if existentes.exists():
                errores["nombre"] = "La Malla curricular ya ha sido registrada"

        if errores:
            raise forms.ValidationError(errores)

        return cleaned_data


# Reemplazar FormularioUnidadCurricular en django/academico/forms.py

class FormularioUnidadCurricular(forms.ModelForm):
    areas_de_conocimiento_texto = forms.CharField(
        label="Áreas de conocimiento",
        required=False,
        widget=forms.TextInput(attrs={
        }),
        help_text="Registre la información separada por comas"
    )

    class Meta:
        model = UnidadCurricular
        fields = (
            "malla_curricular",
            "codigo_de_unidad",
            "nombre",
            "horas_totales",
            "horas_sincronicas",
            "horas_asincronicas",
            "tipo_de_componente",
            "criterio_de_aprobacion",
            "porcentaje_minimo_asistencia",
        )
        labels = {
            "malla_curricular": "Malla curricular registrada",
            "codigo_de_unidad": "Código de Unidad curricular",
            "nombre": "Nombre",
            "horas_totales": "Horas totales",
            "horas_sincronicas": "Horas sincrónicas",
            "horas_asincronicas": "Horas asincrónicas",
            "tipo_de_componente": "Tipo de componente",
            "criterio_de_aprobacion": "Criterio de aprobación",
            "porcentaje_minimo_asistencia": "Porcentaje mínimo de asistencia",
        }
        widgets = {
            "codigo_de_unidad": forms.TextInput(attrs={
                "placeholder": "El código será determinado de forma automática",
                "style": "background-color: #f5f5f7; color: #86868b; pointer-events: none;",
                "readonly": True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

        # Si es edición, cargar las áreas actuales en el campo de texto
        if self.instance and self.instance.pk and self.instance.area_de_conocimiento:
            self.fields["areas_de_conocimiento_texto"].initial = ", ".join(
                self.instance.area_de_conocimiento
            )

    def clean(self):
        from poo.clases.unidad_curricular import UnidadCurricular as UnidadCurricularBase
        from poo.clases.enums.tipo_de_componente import TipoDeComponente

        cleaned_data = super().clean()
        errores = {}

        campos_requeridos = [
            "malla_curricular",
            "nombre",
            "horas_totales",
            "horas_sincronicas",
            "horas_asincronicas",
            "tipo_de_componente",
            "criterio_de_aprobacion",
            "porcentaje_minimo_asistencia",
        ]

        for campo in campos_requeridos:
            if cleaned_data.get(campo) is None or cleaned_data.get(campo) == "":
                errores[campo] = "Información requerida"

        areas_texto = cleaned_data.get("areas_de_conocimiento_texto", "")
        if not areas_texto or not areas_texto.strip():
            errores["areas_de_conocimiento_texto"] = "Información requerida"

        if errores:
            raise forms.ValidationError(errores)

        # Validación a través de la capa POO
        try:
            enum_tipo = TipoDeComponente(cleaned_data.get("tipo_de_componente"))
        except (ValueError, KeyError):
            raise forms.ValidationError({"tipo_de_componente": "Tipo de componente no válido"})

        areas_lista = [a.strip() for a in areas_texto.split(",") if a.strip()]

        unidad_poo = UnidadCurricularBase(
            codigo_de_unidad="PENDIENTE",
            nombre=cleaned_data.get("nombre", ""),
            area_de_conocimiento=areas_lista,
            horas_totales=cleaned_data.get("horas_totales", 0),
            horas_sincronicas=cleaned_data.get("horas_sincronicas", 0),
            horas_asincronicas=cleaned_data.get("horas_asincronicas", 0),
            tipo_de_componente=enum_tipo,
            criterio_de_aprobacion=cleaned_data.get("criterio_de_aprobacion", 7.0),
            porcentaje_minimo_asistencia=cleaned_data.get("porcentaje_minimo_asistencia", 70.0),
        )

        errores_poo = unidad_poo.validar_datos_de_registro()
        if errores_poo:
            raise forms.ValidationError(errores_poo)

        cleaned_data["area_de_conocimiento"] = areas_lista
        return cleaned_data

    def save(self, commit=True):
        instancia = super().save(commit=False)
        instancia.area_de_conocimiento = self.cleaned_data.get("area_de_conocimiento", [])
        if commit:
            instancia.save()
        return instancia


from django.db.models import Q
from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion as PeriodoDeNivelacionBase
from poo.clases.enums.modalidad import Modalidad
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo

class FormularioPeriodoDeNivelacion(forms.ModelForm):
    class Meta:
        model = PeriodoDeNivelacion
        fields = (
            "codigo_periodo", "anio", "numero_periodo", 
            "fecha_inicio", "fecha_fin", "modalidad", "estado"
        )
        labels = {
            "codigo_periodo": "Código de periodo",
            "anio": "Año",
            "numero_periodo": "Número de periodo",
            "fecha_inicio": "Fecha de inicio",
            "fecha_fin": "Fecha de finalización",
            "modalidad": "Modalidad",
            "estado": "Estado",
        }
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}), 
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
            "numero_periodo": forms.NumberInput(attrs={"min": 1, "max": 2})
        }

    def __init__(self, *args, **kwargs):
        self.universidad = kwargs.pop('universidad', None)
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.required = False
            
        self.fields['codigo_periodo'].widget.attrs.update({
            'placeholder': 'El código será determinado de forma automática',
            'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
            'readonly': True
        })

        opciones_originales = list(self.fields['estado'].choices)
        estado_actual = self.instance.estado if (self.instance and self.instance.pk) else None

        if not self.instance.pk:
            opcion_planif = [c for c in opciones_originales if 'PLANIF' in str(c[0]).upper() or 'PLANIF' in str(c[1]).upper()]
            if opcion_planif:
                self.fields['estado'].choices = opcion_planif
                self.initial['estado'] = opcion_planif[0][0]
        else:
            estado_str = str(estado_actual).upper()
            
            if 'PLANIF' in estado_str:
                opcion_planif = [c for c in opciones_originales if 'PLANIF' in str(c[0]).upper() or 'PLANIF' in str(c[1]).upper()]
                self.fields['estado'].choices = opcion_planif
                
            elif 'CURSO' in estado_str:
                opciones_permitidas = [
                    c for c in opciones_originales 
                    if 'CURSO' in str(c[0]).upper() or 'EVALU' in str(c[0]).upper() or 'CURSO' in str(c[1]).upper() or 'EVALU' in str(c[1]).upper()
                ]
                self.fields['estado'].choices = opciones_permitidas
                
            elif 'EVALU' in estado_str:
                opcion_evalu = [c for c in opciones_originales if 'EVALU' in str(c[0]).upper() or 'EVALU' in str(c[1]).upper()]
                self.fields['estado'].choices = opcion_evalu
                
            elif 'CERRADO' in estado_str or 'CIERRA' in estado_str:
                opcion_cerrado = [c for c in opciones_originales if 'CERRADO' in str(c[0]).upper() or 'CERRADO' in str(c[1]).upper()]
                self.fields['estado'].choices = opcion_cerrado
                
                for name, field in self.fields.items():
                    if isinstance(field.widget, (forms.Select, forms.RadioSelect)):
                        field.widget.attrs['disabled'] = True
                    else:
                        field.widget.attrs['readonly'] = True
                        
                    field.widget.attrs['style'] = 'background-color: #f5f5f7; color: #86868b; pointer-events: none;'

    def clean(self):
        if self.instance and self.instance.pk and str(self.instance.estado).upper() in ['CERRADO', 'CIERRA']:
            self.cleaned_data = {
                "codigo_periodo": self.instance.codigo_periodo,
                "anio": self.instance.anio,
                "numero_periodo": self.instance.numero_periodo,
                "fecha_inicio": self.instance.fecha_inicio,
                "fecha_fin": self.instance.fecha_fin,
                "modalidad": self.instance.modalidad,
                "estado": self.instance.estado,
            }
            return self.cleaned_data

        cleaned_data = super().clean()
        errores = {}
        campos_requeridos = ["anio", "numero_periodo", "fecha_inicio", "fecha_fin", "modalidad", "estado"]
        
        for campo in campos_requeridos:
            if not cleaned_data.get(campo):
                errores[campo] = "Información requerida"
                
        fecha_de_inicio = cleaned_data.get("fecha_inicio")
        fecha_de_finalizacion = cleaned_data.get("fecha_fin")
        
        if fecha_de_inicio and fecha_de_finalizacion:
            periodo_poo = PeriodoDeNivelacionBase(
                codigo_periodo="TEMP",
                anio=cleaned_data.get("anio", 2000),
                periodo="TEMP",
                fecha_inicio=fecha_de_inicio,
                fecha_fin=fecha_de_finalizacion,
                modalidad=Modalidad.VIRTUAL,
                numero_periodo=cleaned_data.get("numero_periodo", 1),
                estado=EstadoDePeriodo.PLANIFICACION
            )

            if not periodo_poo.validar_fechas():
                errores["fecha_fin"] = "La fecha de finalización debe ser posterior a la fecha de inicio"
            
            elif self.universidad:
                periodos_chocan = PeriodoDeNivelacion.objects.filter(
                    universidad=self.universidad,
                    fecha_inicio__lte=fecha_de_finalizacion,
                    fecha_fin__gte=fecha_de_inicio
                ).exclude(estado="Cerrado") 
                
                if self.instance and self.instance.pk:
                    periodos_chocan = periodos_chocan.exclude(pk=self.instance.pk)
                    
                if periodos_chocan.exists():
                    errores["fecha_inicio"] = "La fecha especificada presenta conflicto con un Periodo registrado previamente"
                    errores["fecha_fin"] = "La fecha especificada presenta conflicto con un Periodo registrado previamente"

        anio_seleccionado = cleaned_data.get("anio")
        numero_seleccionado = cleaned_data.get("numero_periodo")

        if numero_seleccionado is not None and numero_seleccionado not in (1, 2):
            errores["numero_periodo"] = "Registro no válido (1 o 2)"

        if anio_seleccionado and numero_seleccionado and self.universidad:
            periodos_duplicados = PeriodoDeNivelacion.objects.filter(
                universidad=self.universidad,
                anio=anio_seleccionado,
                numero_periodo=numero_seleccionado,
            )
            if self.instance and self.instance.pk:
                periodos_duplicados = periodos_duplicados.exclude(pk=self.instance.pk)
            if periodos_duplicados.exists():
                errores["numero_periodo"] = "El Periodo de nivelación ya ha sido registrado"
            
        if errores:
            raise forms.ValidationError(errores)
            
        return cleaned_data

    
    
# Reemplazar FormularioParalelo en django/academico/forms.py

class FormularioParalelo(forms.ModelForm):
    class Meta:
        model = Paralelo
        fields = (
            "periodo_de_nivelacion",
            "unidad_curricular",
            "codigo_de_paralelo",
            "nombre",
            "jornada",
            "modalidad",
            "capacidad_maxima",
        )
        labels = {
            "periodo_de_nivelacion": "Periodo de nivelación registrado",
            "unidad_curricular": "Unidad curricular",
            "codigo_de_paralelo": "Código de Paralelo",
            "nombre": "Nombre",
            "jornada": "Jornada",
            "modalidad": "Modalidad",
            "capacidad_maxima": "Número máximo de estudiantes",
        }
        widgets = {
            "codigo_de_paralelo": forms.TextInput(attrs={
                "placeholder": "El código será determinado de forma automática",
                "style": "background-color: #f5f5f7; color: #86868b; pointer-events: none;",
                "readonly": True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        from poo.clases.paralelo import Paralelo as ParaleloBase
        from poo.clases.enums.jornada import Jornada
        from poo.clases.enums.modalidad import Modalidad

        cleaned_data = super().clean()
        errores = {}

        campos_requeridos = [
            "periodo_de_nivelacion",
            "unidad_curricular",
            "nombre",
            "jornada",
            "modalidad",
            "capacidad_maxima",
        ]

        for campo in campos_requeridos:
            if not cleaned_data.get(campo):
                errores[campo] = "Información requerida"

        if errores:
            raise forms.ValidationError(errores)

        # Validación a través de la capa POO
        try:
            enum_jornada = Jornada(cleaned_data.get("jornada"))
            enum_modalidad = Modalidad(cleaned_data.get("modalidad"))
        except ValueError:
            raise forms.ValidationError("Jornada o Modalidad no válida")

        paralelo_poo = ParaleloBase(
            codigo_de_paralelo="PENDIENTE",
            nombre=cleaned_data.get("nombre", ""),
            jornada=enum_jornada,
            modalidad=enum_modalidad,
            capacidad_maxima=cleaned_data.get("capacidad_maxima", 0),
        )

        errores_poo = paralelo_poo.validar_datos_de_registro()
        if errores_poo:
            raise forms.ValidationError(errores_poo)

        return cleaned_data


class FormularioHorario(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ("paralelo", "dia_semana", "hora_inicio", "hora_fin", "espacio_de_imparticion", "modalidad", "numero_semana", "tipo_de_sesion")
        labels = {
            "paralelo": "Paralelo registrado",
            "dia_semana": "Día de semana",
            "hora_inicio": "Hora de inicio",
            "hora_fin": "Hora de finalización",
            "espacio_de_imparticion": "Espacio de impartición",
            "modalidad": "Modalidad",
            "numero_semana": "Número de semana",
            "tipo_de_sesion": "Tipo de sesión",
        }
        widgets = {"hora_inicio": forms.TimeInput(attrs={"type": "time"}), "hora_fin": forms.TimeInput(attrs={"type": "time"})}


class FormularioCohorteDeMatricula(forms.ModelForm):
    class Meta:
        model = CohorteDeMatricula
        fields = ("periodo_de_nivelacion", "carrera_registrada", "codigo_de_registro", "nombre_cohorte", 
                  "fecha_de_cierre", "tipo_de_cohorte", "estado_de_cohorte", "total_primera_matricula", 
                  "total_segunda_matricula", "total_exonerados")
        labels = {
            "periodo_de_nivelacion": "Periodo de nivelación registrado",
            "carrera_registrada": "Carrera registrada",
            "codigo_de_registro": "Código de registro",
            "nombre_cohorte": "Nombre",
            "fecha_de_cierre": "Fecha de cierre",
            "tipo_de_cohorte": "Tipo de Cohorte de matrícula",
            "estado_de_cohorte": "Estado",
            "total_primera_matricula": "Número de primeras matrículas",
            "total_segunda_matricula": "Número de segundas matrículas",
            "total_exonerados": "Número de exonerados",
        }
        widgets = {"fecha_de_cierre": forms.DateInput(attrs={"type": "date"})}


class FormularioMatriculaParalelo(forms.ModelForm):
    class Meta:
        model = MatriculaParalelo
        fields = ("estudiante", "paralelo", "cohorte_de_matricula")
        labels = {
            "estudiante": "Estudiante registrado",
            "paralelo": "Paralelo registrado",
            "cohorte_de_matricula": "Cohorte de matrícula registrada",
        }


class FormularioConsolidadoAcademico(forms.ModelForm):
    class Meta:
        model = ConsolidadoAcademico
        fields = ("periodo_academico", "fecha_de_corte", "total_cupos_aceptados", "registros_totales", "registros_validos", "registros_observados")
        labels = {
            "periodo_academico": "Periodo de nivelación registrado",
            "fecha_de_corte": "Fecha de corte",
            "total_cupos_aceptados": "Número de cupos aceptados",
            "registros_totales": "Número de registros",
            "registros_validos": "Número de registros válidos",
            "registros_observados": "Número de registros observados",
        }
        widgets = {
            "total_cupos_aceptados": forms.NumberInput(attrs={'readonly': True}), #Reestricciones
            "registros_totales": forms.NumberInput(attrs={'readonly': True}),
            "registros_validos": forms.NumberInput(attrs={'readonly': True}),
            "registros_observados": forms.NumberInput(attrs={'readonly': True}),
            
            "fecha_de_corte": forms.DateInput(attrs={"type": "date"}),
        }


class FormularioEvaluacionAcademica(forms.ModelForm):
    class Meta:
        model = EvaluacionAcademica
        fields = ("estudiante", "unidad_curricular", "calificacion_parcial_1", "calificacion_parcial_2", "nota_final", "porcentaje_asistencia", "estado_de_aprobacion", "observacion")
        labels = {
            "estudiante": "Estudiante registrado",
            "unidad_curricular": "Unidad curricular registrada",
            "calificacion_parcial_1": "Calificación primer parcial",
            "calificacion_parcial_2": "Calificación segundo parcial",
            "nota_final": "Calificación final",
            "porcentaje_asistencia": "Porcentaje de asistencia final",
            "estado_de_aprobacion": "Estado de aprobación",
            "observacion": "Observación",
        }
        widgets = {
            #Deshabilitar
            "nota_final": forms.NumberInput(attrs={'readonly': True}),
            "estado_de_aprobacion": forms.TextInput(attrs={'readonly': True}),
        }
        
    def clean_calificacion_parcial_1(self):
        calificacion = self.cleaned_data.get("calificacion_parcial_1")
        if calificacion is not None and not (0.0 <= calificacion <= 10.0):
            raise forms.ValidationError("Calificación no válida (0.0 - 10.0).")
        return calificacion

    def clean_calificacion_parcial_2(self):
        calificacion = self.cleaned_data.get("calificacion_parcial_2")
        if calificacion is not None and not (0.0 <= calificacion <= 10.0):
            raise forms.ValidationError("Calificación no válida (0.0 - 10.0).")
        return calificacion

    def clean_porcentaje_asistencia(self):
        porcentaje = self.cleaned_data.get("porcentaje_asistencia")
        if porcentaje is not None and not (0.0 <= porcentaje <= 100.0):
            raise forms.ValidationError("Porcentaje no válido (0.0 - 100.0).")
        return porcentaje


class FormularioIncidenciaAcademica(forms.ModelForm):
    class Meta:
        model = IncidenciaAcademica
        fields = ("codigo_incidencia", "docente_implicado", "descripcion", "fecha_incidencia", "responsable_autorizacion")
        labels = {
            "codigo_incidencia": "Código de incidencia",
            "docente_implicado": "Docente implicado",
            "descripcion": "Descripción",
            "fecha_incidencia": "Fecha de incidencia",
            "responsable_autorizacion": "Responsable de autorización",
        }
        widgets = {"fecha_incidencia": forms.DateInput(attrs={"type": "date"})}


class FormularioEvaluacionDeDesempeno(forms.ModelForm):
    class Meta:
        model = EvaluacionDeDesempeno
        fields = ("docente_responsable", "periodo_de_nivelacion", "porcentaje_de_horas_cumplidas", 
                  "entrega_oportuna_de_calificaciones", "porcentaje_de_aprobacion_paralelo", 
                  "resultado_de_evaluacion_estudiantil", "puntaje_final")
        labels = {
            "docente_responsable": "Docente responsable",
            "periodo_de_nivelacion": "Periodo de nivelación registrado",
            "porcentaje_de_horas_cumplidas": "Porcentaje de horas cumplidas",
            "entrega_oportuna_de_calificaciones": "Entrega oportuna de calificaciones",
            "porcentaje_de_aprobacion_paralelo": "Porcentaje de aprobación de paralelo",
            "resultado_de_evaluacion_estudiantil": "Resultado de evaluación estudiantil",
            "puntaje_final": "Puntaje final",
        }
        widgets = {
            "puntaje_final": forms.NumberInput(attrs={'readonly': True}),
        }


class FormularioInformeGeneral(forms.ModelForm):
    class Meta:
        model = InformeGeneral
        fields = ("periodo_academico", "codigo_de_informe", "tipo_de_informe", "estado_de_informe", "fecha_de_emision", "cohortes")
        labels = {
            "periodo_academico": "Periodo de nivelación registrado",
            "codigo_de_informe": "Código de informe",
            "tipo_de_informe": "Tipo de informe",
            "estado_de_informe": "Estado",
            "fecha_de_emision": "Fecha de emisión",
            "cohortes": "Cohortes de matrícula",
        }
        widgets = {
            "fecha_de_emision": forms.DateInput(attrs={"type": "date"}),
            "cohortes": forms.CheckboxSelectMultiple(),
            }