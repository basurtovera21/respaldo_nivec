from django import forms
from .models import (Universidad, Campus, Carrera, MallaCurricular, UnidadCurricular, PeriodoDeNivelacion, Paralelo, Horario, CohorteDeMatricula, MatriculaParalelo, ConsolidadoAcademico, EvaluacionAcademica, IncidenciaAcademica, EvaluacionDeDesempeno, InformeGeneral)


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
        cleaned_data = super().clean()
        errores = {}
        
        campos_requeridos = ["nombre", "abreviatura", "codigo_sniese", "direccion_matriz"]

        for campo in campos_requeridos:
            if not cleaned_data.get(campo):
                errores[campo] = "Información requerida"

        if errores:
            raise forms.ValidationError(errores)


class FormularioCampus(forms.ModelForm):
    class Meta:
        model = Campus
        fields = ("codigo_de_campus", "nombre", "direccion_fisica", "provincia")
        labels = {
            "codigo_de_campus": "Código de campus",
            "nombre": "Nombre",
            "direccion_fisica": "Dirección física",
            "provincia": "Provincia",
        }

    def __init__(self, *args, **kwargs):
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
        cleaned_data = super().clean()
        nombre = cleaned_data.get("nombre")
        direccion = cleaned_data.get("direccion_fisica")
        provincia = cleaned_data.get("provincia")

        errores = {}

        if not nombre:
            errores['nombre'] = "Información requerida"
        if not direccion:
            errores['direccion_fisica'] = "Información requerida"
        if not provincia:
            errores['provincia'] = "Información requerida"

        if errores:
            raise forms.ValidationError(errores)

        return cleaned_data


class FormularioCarrera(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = (
            "campus", 
            "codigo_de_carrera", 
            "nombre", 
            "modalidad", 
            "facultad",
            "vigencia_sniese"
        )
        labels = {
            "campus": "Campus registrado",
            "codigo_de_carrera": "Código de carrera",
            "nombre": "Nombre",
            "modalidad": "Modalidad",
            "facultad": "Facultad",
            "vigencia_sniese": "Vigencia SNIESE",
        }
        widgets = {
            "vigencia_sniese": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['campus'].required = False
        self.fields['nombre'].required = False
        self.fields['modalidad'].required = False
        self.fields['facultad'].required = False
        self.fields['vigencia_sniese'].required = False

        self.fields['codigo_de_carrera'].required = False
        self.fields['codigo_de_carrera'].widget.attrs.update({
            'placeholder': 'El código será determinado de forma automática',
            'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
            'readonly': True
        })

    def clean(self):
        cleaned_data = super().clean()
        
        campus = cleaned_data.get("campus")
        nombre = cleaned_data.get("nombre")
        modalidad = cleaned_data.get("modalidad")
        facultad = cleaned_data.get("facultad")
        vigencia_sniese = cleaned_data.get("vigencia_sniese")

        errores = {}

        if not campus:
            errores['campus'] = "Información requerida"
        if not nombre:
            errores['nombre'] = "Información requerida"
        if not modalidad:
            errores['modalidad'] = "Información requerida"
        if not facultad:
            errores['facultad'] = "Información requerida"
        if not vigencia_sniese:
            errores['vigencia_sniese'] = "Información requerida"

        if errores:
            raise forms.ValidationError(errores)

        return cleaned_data


class FormularioMallaCurricular(forms.ModelForm):
    class Meta:
        model = MallaCurricular
        fields = ("carrera", "codigo_de_malla", "nombre", "area_de_conocimiento", "duracion_semanas", 
                  "version_de_malla", "modalidad", "estado", "total_horas_nivelacion")
        labels = {
            "carrera": "Carrera registrada",
            "codigo_de_malla": "Código de malla curricular",
            "nombre": "Nombre",
            "area_de_conocimiento": "Área de conocimiento",
            "duracion_semanas": "Duración (en semanas)",
            "version_de_malla": "Versión de malla curricular",
            "modalidad": "Modalidad",
           "estado": "Estado",
            "total_horas_nivelacion": "Total de horas de nivelación",
        }


class FormularioUnidadCurricular(forms.ModelForm):
    class Meta:
        model = UnidadCurricular
        fields = ("malla_curricular", "codigo_de_unidad", "nombre", "area_de_conocimiento", "horas_totales", 
                  "horas_semanales", "horas_sincronicas", "horas_asincronicas", "tipo_de_componente", 
                  "criterio_de_aprobacion", "porcentaje_minimo_asistencia")
        labels = {
            "malla_curricular": "Malla curricular registrada",
            "codigo_de_unidad": "Código de unidad curricular",
            "nombre": "Nombre",
            "area_de_conocimiento": "Área(s) de conocimiento",
            "horas_totales": "Horas totales",
            "horas_semanales": "Horas semanales",
            "horas_sincronicas": "Horas sincrónicas",
            "horas_asincronicas": "Horas asincrónicas",
            "tipo_de_componente": "Tipo de componente",
            "criterio_de_aprobacion": "Criterio de aprobación",
            "porcentaje_minimo_asistencia": "Porcentaje mínimo de asistencia",
        }

    def clean(self):
        #Validación de horas totales.
        registros = super().clean()
        horas_sincronicas = registros.get("horas_sincronicas", 0)
        horas_asincronicas = registros.get("horas_asincronicas", 0)
        horas_totales = registros.get("horas_totales", 0)
        if (horas_sincronicas + horas_asincronicas) != horas_totales:
            raise forms.ValidationError(f"Las horas registradas deben coincidir con el total de {horas_totales} horas")
        return registros


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
            "fecha_fin": forms.DateInput(attrs={"type": "date"})
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
                    errores["fecha_inicio"] = "La fecha especificada presenta conflicto con un periodo registrado previamente"
                    errores["fecha_fin"] = "La fecha especificada presenta conflicto con un periodo registrado previamente"
            
        if errores:
            raise forms.ValidationError(errores)
            
        return cleaned_data
    
    
class FormularioParalelo(forms.ModelForm):
    class Meta:
        model = Paralelo
        fields = ("periodo_de_nivelacion", "unidad_curricular", "codigo_de_paralelo", "nombre", "jornada", "modalidad", "capacidad_maxima", "docente_responsable")
        labels = {
            "periodo_de_nivelacion": "Periodo de nivelación registrado",
            "unidad_curricular": "Unidad curricular",
            "codigo_de_paralelo": "Código de paralelo",
            "nombre": "Nombre",
            "jornada": "Jornada",
            "modalidad": "Modalidad",
            "capacidad_maxima": "Número máximo de estudiantes",
            "docente_responsable": "Docente responsable",
        }


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
            "tipo_de_cohorte": "Tipo de cohorte de matrícula",
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