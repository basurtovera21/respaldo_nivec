from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from academico.models import Paralelo, Horario, PeriodoDeNivelacion
from academico.services import servicio_registrar_horario, servicio_horas_agendadas_paralelo, servicio_obtener_matriz_de_horarios
from poo.clases.enums.dia_de_semana import DiaDeSemana
from poo.clases.enums.tipo_de_sesion import TipoDeSesion
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

def _parsear_hora(valor):
    try:
        return datetime.strptime(valor, "%H:%M").time()
    except (TypeError, ValueError):
        return None

@requiere_perfil(*ROLES_VISUALIZAN)
def listar_horarios_paralelo(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    horarios = Horario.objects.filter(paralelo=paralelo).order_by(
        "numero_semana", "dia_semana", "hora_inicio"
    )

    horas_agendadas = servicio_horas_agendadas_paralelo(paralelo)
    horas_requeridas = paralelo.unidad_curricular.horas_sincronicas

    return render(request, "academico/horarios_paralelo.html", {
        "paralelo": paralelo,
        "horarios": horarios,
        "horas_agendadas": horas_agendadas,
        "horas_requeridas": horas_requeridas,
        "horas_completas": horas_agendadas >= horas_requeridas,
        "dias": [dia.value for dia in DiaDeSemana],
        "tipos_de_sesion": [tipo.value for tipo in TipoDeSesion],
        "solo_lectura": usuario_es_solo_lectura(request.user),
        "titulo_pagina": "Horario - NIVEC",
        "titulo": f"Horarios - {paralelo.nombre} ({paralelo.unidad_curricular.nombre})",
    })

@requiere_perfil(*ROLES_MODIFICAN)
def registrar_horario(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    if request.method == "POST":
        dia_semana = request.POST.get("dia_semana")
        tipo_de_sesion = request.POST.get("tipo_de_sesion")
        espacio = (request.POST.get("espacio_de_imparticion") or "").strip()
        numero_semana = request.POST.get("numero_semana")
        hora_inicio = _parsear_hora(request.POST.get("hora_inicio"))
        hora_fin = _parsear_hora(request.POST.get("hora_fin"))

        if not hora_inicio or not hora_fin:
            messages.error(request, "Las horas de inicio y finalización son requeridas")
            return redirect("listar_horarios_paralelo", paralelo_id=paralelo.id)

        ok, mensaje = servicio_registrar_horario(
            paralelo, dia_semana, hora_inicio, hora_fin, espacio, numero_semana, tipo_de_sesion
        )
        if ok:
            messages.success(request, mensaje)
        else:
            messages.error(request, mensaje)

    return redirect("listar_horarios_paralelo", paralelo_id=paralelo.id)

@requiere_perfil(*ROLES_MODIFICAN)
def eliminar_horario(request, horario_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    horario = get_object_or_404(
        Horario, id=horario_id,
        paralelo__periodo_de_nivelacion__universidad=universidad_usuario,
    )
    paralelo_id = horario.paralelo_id
    horario.delete()
    messages.success(request, "El horario ha sido eliminado correctamente")
    return redirect("listar_horarios_paralelo", paralelo_id=paralelo_id)

@requiere_perfil(*ROLES_VISUALIZAN)
def matriz_horarios(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    periodos = PeriodoDeNivelacion.objects.filter(
        universidad=universidad_usuario
    ).order_by("-anio", "numero_periodo")

    periodo_id = request.GET.get("periodo") or None
    grupo_clave = request.GET.get("grupo") or None

    periodo_seleccionado = None
    grupos = []
    matriz = []

    if periodo_id:
        periodo_seleccionado = get_object_or_404(
            PeriodoDeNivelacion, id=periodo_id, universidad=universidad_usuario
        )

        paralelos = Paralelo.objects.filter(
            periodo_de_nivelacion=periodo_seleccionado
        ).select_related("unidad_curricular__malla_curricular__carrera")

        grupos_vistos = {}
        for p in paralelos:
            carrera = p.unidad_curricular.malla_curricular.carrera
            clave = f"{carrera.id}|{p.jornada}|{p.nombre}"
            if clave not in grupos_vistos:
                grupos_vistos[clave] = {
                    "clave": clave,
                    "carrera": carrera.nombre,
                    "jornada": p.get_jornada_display(),
                    "nombre": p.nombre,
                }
        grupos = list(grupos_vistos.values())

        if grupo_clave and grupo_clave in grupos_vistos:
            carrera_id, jornada_valor, nombre_valor = grupo_clave.split("|", 2)
            paralelos_grupo = paralelos.filter(
                unidad_curricular__malla_curricular__carrera_id=carrera_id,
                jornada=jornada_valor,
                nombre=nombre_valor,
            )
            matriz = servicio_obtener_matriz_de_horarios(periodo_seleccionado, paralelos_grupo)

    return render(request, "academico/matriz_horarios.html", {
        "periodos": periodos,
        "periodo_seleccionado": periodo_seleccionado,
        "grupos": grupos,
        "grupo_seleccionado": grupo_clave,
        "matriz": matriz,
        "titulo_pagina": "Horario - NIVEC",
        "titulo": "Matriz de horarios",
    })