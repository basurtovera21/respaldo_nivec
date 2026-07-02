from django.db import models

from poo.clases.enums.modalidad import Modalidad
from poo.clases.enums.estado_de_malla import EstadoDeMalla
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo
from poo.clases.enums.jornada import Jornada
from poo.clases.enums.dia_de_semana import DiaDeSemana
from poo.clases.enums.tipo_de_cohorte import TipoDeCohorte
from poo.clases.enums.estado_de_cohorte import EstadoDeCohorte
from poo.clases.enums.estado_de_aprobacion import EstadoDeAprobacion
from poo.clases.enums.tipo_de_informe import TipoDeInforme
from poo.clases.enums.estado_de_informe import EstadoDeInforme


def cambiar_enum_a_choices(enum_clase):
    lista_de_opciones = []
    for opcion in enum_clase:
        tupla_opcion = (opcion.value, opcion.value) #Tupla de dos elementos (valor en base de datos, valor en sistema)
        lista_de_opciones.append(tupla_opcion)
        
    return lista_de_opciones


class Universidad(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la institución")
    abreviatura = models.CharField(max_length=20, verbose_name="Abreviatura")
    codigo_sniese = models.CharField(max_length=50, unique=True, verbose_name="Código SNIESE")
    direccion_matriz = models.CharField(max_length=300, verbose_name="Dirección de matriz")
    identificador_visual = models.ImageField(upload_to="logos/", null=True, blank=True, verbose_name="Identificador visual")

    class Meta:
        verbose_name = "Universidad"
        verbose_name_plural = "Universidades"

    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"


class Campus(models.Model):
    universidad = models.ForeignKey(Universidad, on_delete=models.PROTECT, related_name="campus", verbose_name="Universidad registrada")
    codigo_de_campus = models.CharField(max_length=50, unique=True, verbose_name="Código de campus")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    direccion_fisica = models.CharField(max_length=300, verbose_name="Dirección física")
    provincia = models.CharField(max_length=100, verbose_name="Provincia")

    class Meta:
        verbose_name = "Campus"
        verbose_name_plural = "Campus"

    def __str__(self):
        return self.nombre


class Carrera(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, related_name="carreras", verbose_name="Campus registrado")
    codigo_de_carrera = models.CharField(max_length=50, unique=True, verbose_name="Código de carrera")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    modalidad = models.CharField(max_length=50, choices=cambiar_enum_a_choices(Modalidad), verbose_name="Modalidad")
    vigencia_sniese = models.DateField(verbose_name="Vigencia SNIESE")

    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"

    def __str__(self):
        return self.nombre


class MallaCurricular(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT, related_name="mallas_curriculares", verbose_name="Carrera registrada")
    codigo_de_malla = models.CharField(max_length=50, unique=True, verbose_name="Código de Malla curricular")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    version_de_malla = models.CharField(max_length=20, verbose_name="Versión de Malla curricular")
    estado = models.CharField(max_length=50, choices=cambiar_enum_a_choices(EstadoDeMalla), default=EstadoDeMalla.DISENO.value, verbose_name="Estado")
    total_horas_nivelacion = models.FloatField(default=0.0, verbose_name="Total de horas de nivelación")

    class Meta:
        verbose_name = "Malla curricular"
        verbose_name_plural = "Mallas curriculares"

    def __str__(self):
        return f"{self.codigo_de_malla} ({self.nombre})"



class UnidadCurricular(models.Model):
    malla_curricular = models.ForeignKey(MallaCurricular, on_delete=models.PROTECT, related_name="unidades_curriculares", verbose_name="Malla curricular registrada")
    codigo_de_unidad = models.CharField(max_length=50, unique=True, verbose_name="Código de unidad curricular")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    horas_totales = models.FloatField(verbose_name="Horas totales")
    horas_sincronicas = models.FloatField(verbose_name="Horas sincrónicas")
    horas_sincronicas_semanales = models.FloatField(default=0, verbose_name="Horas sincrónicas semanales")
    horas_asincronicas = models.FloatField(verbose_name="Horas asincrónicas")
    criterio_de_aprobacion = models.FloatField(default=7.0, verbose_name="Criterio de aprobación")
    porcentaje_minimo_asistencia = models.FloatField(default=70.0, verbose_name="Porcentaje mínimo de asistencia")

    class Meta:
        verbose_name = "Unidad curricular"
        verbose_name_plural = "Unidades curriculares"

    def __str__(self):
        return f"{self.codigo_de_unidad} ({self.nombre})"


class PeriodoDeNivelacion(models.Model):
    universidad = models.ForeignKey(Universidad, on_delete=models.PROTECT, related_name="periodos_de_nivelacion", verbose_name="Universidad registrada")
    codigo_periodo = models.CharField(max_length=50, unique=True, verbose_name="Código de periodo de nivelación")
    anio = models.IntegerField(verbose_name="Año")
    periodo = models.CharField(max_length=50, verbose_name="Periodo")
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de finalización")
    modalidad = models.CharField(max_length=50, choices=cambiar_enum_a_choices(Modalidad), verbose_name="Modalidad")
    numero_periodo = models.IntegerField(verbose_name="Número de periodo de nivelación")
    estado = models.CharField(max_length=50, choices=cambiar_enum_a_choices(EstadoDePeriodo), default=EstadoDePeriodo.PLANIFICACION.value, verbose_name="Estado")

    class Meta:
        verbose_name = "Periodo de nivelación"
        verbose_name_plural = "Periodos de nivelación"

    def __str__(self):
        return f"{self.periodo} ({self.estado})"


class Paralelo(models.Model):
    periodo_de_nivelacion = models.ForeignKey(PeriodoDeNivelacion, on_delete=models.PROTECT, related_name="paralelos", verbose_name="Periodo de nivelación registrado")
    unidad_curricular = models.ForeignKey(UnidadCurricular, on_delete=models.PROTECT, related_name="paralelos", verbose_name="Unidad curricular")
    codigo_de_paralelo = models.CharField(max_length=50, verbose_name="Código de paralelo")
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    jornada = models.CharField(max_length=50, choices=cambiar_enum_a_choices(Jornada), verbose_name="Jornada")
    modalidad = models.CharField(max_length=50, choices=cambiar_enum_a_choices(Modalidad), verbose_name="Modalidad")
    capacidad_maxima = models.IntegerField(default=35, verbose_name="Número máximo de estudiantes")
    
    docente_responsable = models.ForeignKey('usuarios.PerfilDocente', on_delete=models.SET_NULL, null=True, blank=True, related_name="paralelos", verbose_name="Docente responsable")

    class Meta:
        verbose_name = "Paralelo"
        verbose_name_plural = "Paralelos"

    def __str__(self):
        return f"{self.nombre} ({self.unidad_curricular.nombre})"
    
    def tiene_cupo_disponible(self):
        total_matriculados = self.estudiantes_matriculados.count()
        return total_matriculados < self.capacidad_maxima


class Horario(models.Model):
    paralelo = models.ForeignKey(Paralelo, on_delete=models.CASCADE, related_name="horarios", verbose_name="Paralelo registrado")
    dia_semana = models.CharField(max_length=20, choices=cambiar_enum_a_choices(DiaDeSemana), verbose_name="Día de semana")
    hora_inicio = models.TimeField(verbose_name="Hora de inicio")
    hora_fin = models.TimeField(verbose_name="Hora de finalización")
    espacio_de_imparticion = models.CharField(max_length=200, blank=True, default="", verbose_name="Espacio de impartición")

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"

    def __str__(self):
        return f"{self.dia_semana}: {self.hora_inicio}-{self.hora_fin} ({self.paralelo.nombre})"
    
    def determinar_duracion_horas(self):
        from poo.clases.horario import Horario as HorarioBase
        from poo.clases.enums.dia_de_semana import DiaDeSemana as DiaBase
        
        horario = HorarioBase(
            dia_semana=DiaBase(self.dia_semana),
            hora_inicio=self.hora_inicio,
            hora_fin=self.hora_fin,
            espacio_de_imparticion=self.espacio_de_imparticion,
        )
        return horario.determinar_duracion_horas()


class CohorteDeMatricula(models.Model):
    periodo_de_nivelacion = models.ForeignKey(PeriodoDeNivelacion, on_delete=models.PROTECT, related_name="cohortes_de_matricula", verbose_name="Periodo de nivelación registrado")
    carrera_registrada = models.ForeignKey(Carrera, on_delete=models.PROTECT, related_name="cohortes", verbose_name="Carrera registrada")
    codigo_de_registro = models.CharField(max_length=50, unique=True, verbose_name="Código de registro")
    nombre_cohorte = models.CharField(max_length=200, verbose_name="Nombre")
    fecha_de_cierre = models.DateField(verbose_name="Fecha de cierre")
    tipo_de_cohorte = models.CharField(max_length=50, choices=cambiar_enum_a_choices(TipoDeCohorte), verbose_name="Tipo de cohorte de matrícula")
    estado_de_cohorte = models.CharField(max_length=50, choices=cambiar_enum_a_choices(EstadoDeCohorte), default=EstadoDeCohorte.ABIERTA.value, verbose_name="Estado")
    total_primera_matricula = models.IntegerField(default=0, verbose_name="Número de primeras matrículas")
    total_segunda_matricula = models.IntegerField(default=0, verbose_name="Número de segundas matrículas")
    total_exonerados = models.IntegerField(default=0, verbose_name="Número de exonerados")

    class Meta:
        verbose_name = "Cohorte de matrícula"
        verbose_name_plural = "Cohortes de matrícula"

    def __str__(self):
        return f"{self.codigo_de_registro} ({self.tipo_de_cohorte})"
    
    def calcular_total_matriculados(self):
        #poo/
        from poo.clases.cohorte_de_matricula import CohorteDeMatricula as CohorteDeMatriculaBase
        from poo.clases.enums.tipo_de_cohorte import TipoDeCohorte as TipoCohorteBase
        
        cohorte_de_matricula = CohorteDeMatriculaBase(
            codigo_de_registro=self.codigo_de_registro,
            periodo_de_nivelacion=None, #No se necesita para la suma
            carrera_registrada=None, #No se necesita para la suma
            fecha_de_cierre=self.fecha_de_cierre,
            tipo_de_cohorte=TipoCohorteBase(self.tipo_de_cohorte)
        )
        
        cohorte_de_matricula.total_primera_matricula = self.total_primera_matricula
        cohorte_de_matricula.total_segunda_matricula = self.total_segunda_matricula
        cohorte_de_matricula.total_exonerados = self.total_exonerados
        
        return cohorte_de_matricula.calcular_total_matriculados()


class MatriculaParalelo(models.Model): 
    estudiante = models.ForeignKey('usuarios.PerfilEstudiante', on_delete=models.PROTECT, related_name="estudiantes_matriculados", verbose_name="Estudiante registrado")
    paralelo = models.ForeignKey(Paralelo, on_delete=models.PROTECT, related_name="estudiantes_matriculados", verbose_name="Paralelo registrado")
    cohorte_de_matricula = models.ForeignKey(CohorteDeMatricula, on_delete=models.PROTECT, related_name="matriculas", verbose_name="Cohorte de matrícula registrada")
    fecha_registro = models.DateField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        verbose_name = "Matrícula en paralelo"
        verbose_name_plural = "Matrículas en paralelos"
        unique_together = ("estudiante", "paralelo")

    def __str__(self):
        return f"{self.estudiante} ({self.paralelo})"


class ConsolidadoAcademico(models.Model):
    periodo_academico = models.OneToOneField(PeriodoDeNivelacion, on_delete=models.PROTECT, related_name="consolidado_academico", verbose_name="Periodo de nivelación registrado")
    fecha_de_corte = models.DateField(verbose_name="Fecha de corte")
    total_cupos_aceptados = models.IntegerField(default=0, verbose_name="Número de cupos aceptados")
    registros_totales = models.IntegerField(default=0, verbose_name="Número de registros")
    registros_validos = models.IntegerField(default=0, verbose_name="Número de registros válidos")
    registros_observados = models.IntegerField(default=0, verbose_name="Número de registros observados")

    class Meta:
        verbose_name = "Consolidado académico"
        verbose_name_plural = "Consolidados académicos"

    def __str__(self):
        return f"CONSOLIDADO ACADÉMICO ({self.periodo_academico.periodo})"


class EvaluacionAcademica(models.Model):
    estudiante = models.ForeignKey('usuarios.PerfilEstudiante', on_delete=models.PROTECT, related_name="evaluaciones_academicas", verbose_name="Estudiante registrado")
    unidad_curricular = models.ForeignKey(UnidadCurricular, on_delete=models.PROTECT, related_name="evaluaciones_academicas", verbose_name="Unidad curricular registrada")
    calificacion_parcial_1 = models.FloatField(default=0.0, verbose_name="Calificación primer parcial")
    calificacion_parcial_2 = models.FloatField(default=0.0, verbose_name="Calificación segundo parcial")
    nota_final = models.FloatField(default=0.0, verbose_name="Calificación final")
    porcentaje_asistencia = models.FloatField(default=0.0,  verbose_name="Porcentaje de asistencia final")
    estado_de_aprobacion = models.CharField(max_length=50, choices=cambiar_enum_a_choices(EstadoDeAprobacion), default=EstadoDeAprobacion.PENDIENTE.value,  verbose_name="Estado de aprobación")
    observacion = models.TextField(blank=True, default="",  verbose_name="Observación")

    class Meta:
        verbose_name = "Evaluación académica"
        verbose_name_plural = "Evaluaciones académicas"
        unique_together = ("estudiante", "unidad_curricular") 

    def __str__(self):
        return f"{self.estudiante} ({self.unidad_curricular.nombre})"
    

class IncidenciaAcademica(models.Model):
    codigo_incidencia = models.CharField(max_length=50, unique=True, verbose_name="Código de incidencia")
    docente_implicado = models.ForeignKey('usuarios.PerfilDocente', on_delete=models.PROTECT, related_name="incidencias", verbose_name="Docente implicado")
    descripcion = models.TextField(verbose_name="Descripción")
    fecha_incidencia = models.DateField( verbose_name="Fecha de incidencia")
    responsable_autorizacion = models.ForeignKey('usuarios.PerfilAdministrativo', on_delete=models.PROTECT, related_name="incidencias_autorizadas",  verbose_name="Responsable de autorización")

    class Meta:
        verbose_name = "Incidencia académica"
        verbose_name_plural = "Incidencias académicas"

    def __str__(self):
        return f"{self.codigo_incidencia} ({self.docente_implicado})"
    
    
class EvaluacionDeDesempeno(models.Model):
    docente_responsable = models.ForeignKey('usuarios.PerfilDocente', on_delete=models.PROTECT, related_name="evaluaciones_desempeno",  verbose_name="Docente responsable")
    periodo_de_nivelacion = models.ForeignKey(PeriodoDeNivelacion, on_delete=models.PROTECT, related_name="evaluaciones_desempeno", verbose_name="Periodo de nivelación registrado")
    porcentaje_de_horas_cumplidas = models.FloatField(default=0.0, verbose_name="Porcentaje de horas cumplidas")
    entrega_oportuna_de_calificaciones = models.BooleanField(default=False, verbose_name="Entrega oportuna de calificaciones")
    porcentaje_de_aprobacion_paralelo = models.FloatField(default=0.0, verbose_name="Porcentaje de aprobación de paralelo")
    resultado_de_evaluacion_estudiantil = models.FloatField(default=0.0, verbose_name="Resultado de evaluación estudiantil")
    puntaje_final = models.FloatField(default=0.0,  verbose_name="Puntaje final")

    class Meta:
        verbose_name = "Evaluación de desempeño"
        verbose_name_plural = "Evaluaciones de desempeño"
        unique_together = ("docente_responsable", "periodo_de_nivelacion")

    def __str__(self):
        return f"{self.docente_responsable} ({self.periodo_de_nivelacion.periodo})"    
    
    
class InformeGeneral(models.Model):
    periodo_academico = models.ForeignKey(PeriodoDeNivelacion, on_delete=models.PROTECT, related_name="informes", verbose_name="Periodo de nivelación registrado")
    codigo_de_informe = models.CharField(max_length=100, unique=True, verbose_name="Código de informe")
    tipo_de_informe = models.CharField(max_length=50, choices=cambiar_enum_a_choices(TipoDeInforme), verbose_name="Tipo de informe")
    estado_de_informe = models.CharField(max_length=50, choices=cambiar_enum_a_choices(EstadoDeInforme), default=EstadoDeInforme.BORRADOR.value, verbose_name="Estado")
    fecha_de_emision = models.DateField(null=True, blank=True, verbose_name="Fecha de emisión")
    cohortes = models.ManyToManyField(CohorteDeMatricula, blank=True, related_name="informes", verbose_name="Cohortes de matrícula")

    class Meta:
        verbose_name = "Informe general"
        verbose_name_plural = "Informes generales"

    def __str__(self):
        return f"{self.codigo_de_informe} ({self.estado_de_informe})"