from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import openpyxl
from django.http import HttpResponse
from usuarios.utils import generar_identificador_siguiente

from .models import (Universidad, Campus, Carrera, MallaCurricular, UnidadCurricular,
                     PeriodoDeNivelacion, Paralelo, Horario, CohorteDeMatricula,
                     MatriculaParalelo, ConsolidadoAcademico, EvaluacionAcademica,
                     IncidenciaAcademica, EvaluacionDeDesempeno, InformeGeneral)
from .forms import (FormularioUniversidad, FormularioCampus, FormularioCarrera,
                    FormularioMallaCurricular, FormularioUnidadCurricular,
                    FormularioPeriodoDeNivelacion, FormularioParalelo, FormularioHorario,
                    FormularioCohorteDeMatricula, FormularioMatriculaParalelo,
                    FormularioConsolidadoAcademico, FormularioEvaluacionAcademica,
                    FormularioIncidenciaAcademica, FormularioEvaluacionDeDesempeno,
                    FormularioInformeGeneral)
from . import services
from datetime import datetime, date

#Estructura académica
@login_required
def listar_mallas(request):
    mallas = MallaCurricular.objects.all().select_related("carrera")
    return render(request, "academico/listar_mallas.html", {"mallas": mallas})


@login_required
def registrar_malla(request):
    if request.method == "POST":
        formulario = FormularioMallaCurricular(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Malla curricular registrada correctamente.")
            return redirect("listar_mallas")
    else:
        formulario = FormularioMallaCurricular()
    return render(request, "academico/formulario_malla.html", {
        "formulario": formulario,
        "titulo": "Registrar malla curricular",
    })


@login_required
def listar_unidades(request):
    unidades = UnidadCurricular.objects.all().select_related("malla_curricular")
    return render(request, "academico/listar_unidades.html", {"unidades": unidades})


@login_required
def registrar_unidad(request):
    if request.method == "POST":
        formulario = FormularioUnidadCurricular(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Unidad curricular registrada correctamente.")
            return redirect("listar_unidades")
    else:
        formulario = FormularioUnidadCurricular()
    return render(request, "academico/formulario_unidad.html", {
        "formulario": formulario,
        "titulo": "Registrar unidad curricular",
    })

@login_required
def listar_paralelos(request):
    paralelos = Paralelo.objects.all().select_related(
        "periodo_de_nivelacion", "unidad_curricular", "docente_responsable"
    )
    return render(request, "academico/listar_paralelos.html", {"paralelos": paralelos})

@login_required
def registrar_paralelo(request):
    if request.method == "POST":
        formulario = FormularioParalelo(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Paralelo registrado correctamente.")
            return redirect("listar_paralelos")
    else:
        formulario = FormularioParalelo()
    return render(request, "academico/formulario_paralelo.html", {
        "formulario": formulario,
        "titulo": "Registrar paralelo",
    })


@login_required
def registrar_horario(request):
    if request.method == "POST":
        formulario = FormularioHorario(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Horario registrado correctamente.")
            return redirect("listar_paralelos")
    else:
        formulario = FormularioHorario()
    return render(request, "academico/formulario_horario.html", {
        "formulario": formulario,
        "titulo": "Registrar horario",
    })


#Procesos académicos
@login_required
def listar_cohortes(request):
    cohortes = CohorteDeMatricula.objects.all().select_related(
        "periodo_de_nivelacion", "carrera_registrada"
    )
    return render(request, "academico/listar_cohortes.html", {"cohortes": cohortes})


@login_required
def registrar_cohorte(request):
    if request.method == "POST":
        formulario = FormularioCohorteDeMatricula(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Cohorte de matrícula registrada correctamente.")
            return redirect("listar_cohortes")
    else:
        formulario = FormularioCohorteDeMatricula()
    return render(request, "academico/formulario_cohorte.html", {
        "formulario": formulario,
        "titulo": "Registrar cohorte de matrícula",
    })


@login_required
def registrar_matricula(request):
    if request.method == "POST":
        formulario = FormularioMatriculaParalelo(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Matrícula en paralelo registrada correctamente.")
            return redirect("listar_paralelos")
    else:
        formulario = FormularioMatriculaParalelo()
    return render(request, "academico/formulario_matricula.html", {
        "formulario": formulario,
        "titulo": "Registrar matrícula en paralelo",
    })


@login_required
def procesar_mtn(request):
    from academico.forms import FormularioConsolidadoAcademico
    if request.method == "POST" and request.FILES.get("documento_mtn"):
        periodo_id = request.POST.get("periodo")
        periodo = get_object_or_404(PeriodoDeNivelacion, pk=periodo_id)
        resultado = services.servicio_procesar_mtn(request.FILES["documento_mtn"], periodo)
        messages.success(
            request,
            f"MTN procesada: {resultado['registros_validos']} válidos, "
            f"{resultado['registros_observados']} observados de {resultado['registros_totales']}."
        )
        for observacion in resultado["filas_observadas"]:
            messages.warning(request, observacion)
        return redirect("listar_estudiantes")
    periodos = PeriodoDeNivelacion.objects.filter(estado="Planificación")
    return render(request, "dan/cargar_mtn.html", {
        "periodos": periodos,
        "titulo": "Procesar Matriz de Tercer Nivel (MTN)",
    })


@login_required
def distribuir_estudiantes(request, periodo_id):
    periodo = get_object_or_404(PeriodoDeNivelacion, pk=periodo_id)
    no_asignados = services.servicio_distribuir_estudiantes(periodo)
    if no_asignados:
        messages.warning(request, f"{len(no_asignados)} estudiante(s) sin paralelo disponible.")
    else:
        messages.success(request, "Todos los estudiantes fueron asignados correctamente.")
    return redirect("listar_paralelos")


@login_required
def listar_evaluaciones(request):
    evaluaciones = EvaluacionAcademica.objects.all().select_related(
        "estudiante", "unidad_curricular"
    )
    return render(request, "academico/listar_evaluaciones.html", {"evaluaciones": evaluaciones})

@login_required
def registrar_evaluacion(request):
    if request.method == "POST":
        formulario = FormularioEvaluacionAcademica(request.POST)
        if formulario.is_valid():
            evaluacion = formulario.save(commit=False)
            evaluacion.save()
            services.servicio_registrar_evaluacion(evaluacion)
            messages.success(request, "Evaluación registrada correctamente.")
            return redirect("listar_evaluaciones")
    else:
        formulario = FormularioEvaluacionAcademica()
    return render(request, "academico/formulario_evaluacion.html", {
        "formulario": formulario,
        "titulo": "Registrar evaluación académica",
    })


@login_required
def listar_incidencias(request):
    incidencias = IncidenciaAcademica.objects.all().select_related(
        "docente_implicado", "responsable_autorizacion"
    )
    return render(request, "academico/listar_incidencias.html", {"incidencias": incidencias})

@login_required
def registrar_incidencia(request):
    if request.method == "POST":
        formulario = FormularioIncidenciaAcademica(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Incidencia registrada correctamente.")
            return redirect("listar_incidencias")
    else:
        formulario = FormularioIncidenciaAcademica()
    return render(request, "academico/formulario_incidencia.html", {
        "formulario": formulario,
        "titulo": "Registrar incidencia académica",
    })


@login_required
def registrar_desempeno(request):
    if request.method == "POST":
        formulario = FormularioEvaluacionDeDesempeno(request.POST)
        if formulario.is_valid():
            evaluacion = formulario.save(commit=False)
            from poo.servicios.estrategia_de_evaluacion_estandar import EstrategiaDeEvaluacionEstandar
            estrategia = EstrategiaDeEvaluacionEstandar(
                porcentaje_horas = 0.25,
                porcentaje_notas = 0.25,
                porcentaje_aprobacion = 0.25,
                porcentaje_evaluacion_estudiantil = 0.25
            )
            from poo.clases.evaluacion_de_desempeno import EvaluacionDeDesempeno as EvaluacionDeDesempenoPOO
            evaluacion_poo = EvaluacionDeDesempenoPOO(
                docente_responsable = None,
                porcentaje_de_horas_cumplidas = evaluacion.porcentaje_de_horas_cumplidas,
                entrega_oportuna_de_calificaciones = evaluacion.entrega_oportuna_de_calificaciones,
                porcentaje_de_aprobacion_paralelo = evaluacion.porcentaje_de_aprobacion_paralelo,
                resultado_de_evaluacion_estudiantil = evaluacion.resultado_de_evaluacion_estudiantil
            )
            evaluacion.puntaje_final = evaluacion_poo.procesar_evaluacion(estrategia)
            evaluacion.save()
            messages.success(request, "Evaluación de desempeño registrada correctamente.")
            return redirect("listar_docentes")
    else:
        formulario = FormularioEvaluacionDeDesempeno()
    return render(request, "academico/formulario_desempeno.html", {
        "formulario": formulario,
        "titulo": "Registrar evaluación de desempeño",
    })


#Informes
@login_required
def listar_informes(request):
    informes = InformeGeneral.objects.all().select_related("periodo_academico")
    return render(request, "academico/listar_informes.html", {"informes": informes})


@login_required
def registrar_informe(request):
    if request.method == "POST":
        formulario = FormularioInformeGeneral(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Informe registrado correctamente.")
            return redirect("listar_informes")
    else:
        formulario = FormularioInformeGeneral()
    return render(request, "academico/formulario_informe.html", {
        "formulario": formulario,
        "titulo": "Registrar informe general",
    })


@login_required
def emitir_informe(request, informe_id):
    informe = get_object_or_404(InformeGeneral, pk=informe_id)
    from poo.clases.informe_general import InformeGeneral as InformeGeneralPOO
    from poo.clases.enums.tipo_de_informe import TipoDeInforme
    from poo.clases.periodo_de_nivelacion import PeriodoDeNivelacion as PeriodoDeNivelacionBase
    from poo.clases.enums.modalidad import Modalidad

    periodo_poo = PeriodoDeNivelacionBase(
        codigo_periodo = informe.periodo_academico.codigo_periodo,
        anio = informe.periodo_academico.anio,
        periodo = informe.periodo_academico.periodo,
        fecha_inicio = informe.periodo_academico.fecha_inicio,
        fecha_fin = informe.periodo_academico.fecha_fin,
        modalidad = Modalidad(informe.periodo_academico.modalidad),
        numero_periodo = informe.periodo_academico.numero_periodo
    )
    periodo_poo._estado = __import__(
        'poo.clases.enums.estado_de_periodo', fromlist=['EstadoDePeriodo']
    ).EstadoDePeriodo(informe.periodo_academico.estado)

    informe_poo = InformeGeneralPOO(
        codigo_de_informe = informe.codigo_de_informe,
        periodo_academico = periodo_poo,
        tipo_de_informe = TipoDeInforme(informe.tipo_de_informe)
    )
    resultado = informe_poo.emitir_informe_de_nivelacion()
    if resultado:
        from datetime import date
        informe.estado_de_informe = "Revisión"
        informe.fecha_de_emision = date.today()
        informe.save()
        messages.success(request, "Informe emitido correctamente.")
    else:
        messages.error(request, "No se pudo emitir el informe. Verifique que el periodo esté cerrado.")
    return redirect("listar_informes")


@login_required
def exportar_informe(request, informe_id):
    informe = get_object_or_404(InformeGeneral, pk=informe_id)
    formato = request.GET.get("formato", "excel")
    return services.servicio_exportar_informe(informe, formato)