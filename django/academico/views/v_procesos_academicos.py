from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from datetime import date

from academico.models import (CohorteDeMatricula, EvaluacionAcademica,
                     IncidenciaAcademica, InformeGeneral)
from academico.forms import (FormularioCohorteDeMatricula, FormularioMatriculaParalelo,
                    FormularioEvaluacionAcademica, FormularioIncidenciaAcademica,
                    FormularioEvaluacionDeDesempeno, FormularioInformeGeneral)
from academico import services


# ═══════════════════════════════════════════════════════════
# PROCESOS ACADÉMICOS
# ═══════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════
# EVALUACIONES
# ═══════════════════════════════════════════════════════════

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
            services.servicio_registrar_evaluacion_academica(evaluacion)
            messages.success(request, "Evaluación registrada correctamente.")
            return redirect("listar_evaluaciones")
    else:
        formulario = FormularioEvaluacionAcademica()
    return render(request, "academico/formulario_evaluacion.html", {
        "formulario": formulario,
        "titulo": "Registrar evaluación académica",
    })


# ═══════════════════════════════════════════════════════════
# INCIDENCIAS
# ═══════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════
# DESEMPEÑO DOCENTE
# ═══════════════════════════════════════════════════════════

@login_required
def registrar_desempeno(request):
    if request.method == "POST":
        formulario = FormularioEvaluacionDeDesempeno(request.POST)
        if formulario.is_valid():
            evaluacion = formulario.save(commit=False)
            from poo.clases.servicios.estrategia_de_evaluacion_estandar import EstrategiaDeEvaluacionEstandar
            estrategia = EstrategiaDeEvaluacionEstandar(
                porcentaje_horas=0.25,
                porcentaje_notas=0.25,
                porcentaje_aprobacion=0.25,
                porcentaje_evaluacion_estudiantil=0.25
            )
            from poo.clases.evaluacion_de_desempeno import EvaluacionDeDesempeno as EvaluacionDeDesempenoPOO
            evaluacion_poo = EvaluacionDeDesempenoPOO(
                docente_responsable=None,
                porcentaje_de_horas_cumplidas=evaluacion.porcentaje_de_horas_cumplidas,
                entrega_oportuna_de_calificaciones=evaluacion.entrega_oportuna_de_calificaciones,
                porcentaje_de_aprobacion_paralelo=evaluacion.porcentaje_de_aprobacion_paralelo,
                resultado_de_evaluacion_estudiantil=evaluacion.resultado_de_evaluacion_estudiantil
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


# ═══════════════════════════════════════════════════════════
# INFORMES
# ═══════════════════════════════════════════════════════════

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
    from poo.clases.enums.estado_de_periodo import EstadoDePeriodo

    periodo_poo = PeriodoDeNivelacionBase(
        codigo_periodo=informe.periodo_academico.codigo_periodo,
        anio=informe.periodo_academico.anio,
        periodo=informe.periodo_academico.periodo,
        fecha_inicio=informe.periodo_academico.fecha_inicio,
        fecha_fin=informe.periodo_academico.fecha_fin,
        numero_periodo=informe.periodo_academico.numero_periodo,
        estado=EstadoDePeriodo(informe.periodo_academico.estado)
    )

    informe_poo = InformeGeneralPOO(
        codigo_de_informe=informe.codigo_de_informe,
        periodo_academico=periodo_poo,
        tipo_de_informe=TipoDeInforme(informe.tipo_de_informe)
    )
    resultado = informe_poo.emitir_informe_de_nivelacion()
    if resultado:
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
