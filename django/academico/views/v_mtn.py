from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
import openpyxl

from academico.models import PeriodoDeNivelacion, ConsolidadoAcademico
from academico.services import servicio_procesar_mtn
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo
from usuarios.utils import (
    requiere_perfil,
    usuario_es_solo_lectura,
    ROL_COORDINADOR_DAN,
    ROL_DIRECTOR_DAN,
    ROL_RECTOR,
    ROL_VICERRECTOR,
)

ROLES_VISUALIZAN = (ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR)
ROLES_MODIFICAN = (ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN)

@requiere_perfil(*ROLES_MODIFICAN)
def descargar_plantilla_mtn(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "MTN"

    cabeceras = [
        "Tipo de identificación (Cédula, Pasaporte, Cédula extranjera)",
        "Número de identificación", "Nombres", "Apellidos", "Correo institucional",
        "Jornada registrada (Matutina, Vespertina, Nocturna)",
        "Registro de cupo (Registro regular, Segunda matrícula, Proceso de exoneración)",
        "Carrera registrada", "Campus registrado",
    ]
    ws.append(cabeceras)

    for col in range(1, len(cabeceras) + 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 40

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="formato_mtn_nivec.xlsx"'
    wb.save(response)
    return response

@requiere_perfil(*ROLES_MODIFICAN)
def procesar_mtn(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    periodos = PeriodoDeNivelacion.objects.filter(
        universidad=universidad_usuario,
        estado=EstadoDePeriodo.PLANIFICACION.value,
    )

    if not periodos.exists():
        messages.warning(request, "No existen periodos de nivelación en Planificación")
        return redirect("panel_dan")

    if request.method == "POST":
        periodo_id = request.POST.get("periodo") or None
        periodo = periodos.filter(id=periodo_id).first() if periodo_id else None
        if not periodo:
            messages.error(request, "Debe seleccionar un Periodo de nivelación en Planificación")
            return redirect("procesar_mtn")

        if "archivo_excel" not in request.FILES:
            messages.error(request, "Debe registrar el documento de la Matriz de Tercer Nivel (MTN)")
            return redirect("procesar_mtn")

        archivo = request.FILES["archivo_excel"]
        if not archivo.name.endswith(".xlsx"):
            messages.error(request, "Documento con formato no válido")
            return redirect("procesar_mtn")

        resultado = servicio_procesar_mtn(archivo, periodo)

        if resultado.get("error"):
            messages.error(request, resultado["error"])
            return redirect("procesar_mtn")

        for advertencia in resultado["advertencias"]:
            messages.warning(request, advertencia)

        if resultado["exitosos"] > 0:
            clasificacion = resultado["clasificacion"]
            messages.success(
                request,
                f"{resultado['exitosos']} partícipe(s) registrado(s) "
                f"({clasificacion['regular']} regular, {clasificacion['segunda']} segunda matrícula, "
                f"{clasificacion['exoneracion']} exoneración). "
                f"{resultado['observados']} registro(s) observado(s)"
            )
        else:
            messages.warning(
                request,
                f"No se registraron partícipes nuevos. {resultado['observados']} registro(s) observado(s)"
            )

        return redirect("listar_consolidados")

    return render(request, "academico/procesar_mtn.html", {
        "periodos": periodos,
        "titulo_pagina": "Procesar MTN - NIVEC",
        "titulo": "Procesar Matriz de Tercer Nivel (MTN)",
        "url_plantilla": "descargar_plantilla_mtn",
        "url_cancelar": "panel_dan",
    })

@requiere_perfil(*ROLES_VISUALIZAN)
def listar_consolidados(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    consolidados = ConsolidadoAcademico.objects.filter(
        periodo_academico__universidad=universidad_usuario
    ).select_related("periodo_academico")

    return render(request, "academico/listar_consolidados.html", {
        "consolidados": consolidados,
        "solo_lectura": usuario_es_solo_lectura(request.user),
        "titulo_pagina": "Consolidados académicos - NIVEC",
        "titulo": "Consolidados académicos",
        "url_registrar": "procesar_mtn",
        "texto_registrar": "Procesar MTN",
        "url_volver": "panel_dan",
    })