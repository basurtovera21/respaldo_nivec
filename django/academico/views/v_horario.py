from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from academico.models import Paralelo, Horario, PeriodoDeNivelacion
from academico.services import servicio_registrar_horario, servicio_horas_agendadas_paralelo, servicio_obtener_matriz_de_horarios, servicio_generar_horario_sugerido, servicio_editar_horario, periodo_en_planificacion, _horas_sincronicas_semanales
from poo.clases.enums.dia_de_semana import DiaDeSemana
from poo.clases.enums.tipo_de_sesion import TipoDeSesion
from poo.clases.enums.jornada import Jornada
from poo.clases.franja_horaria import texto_franja
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

def _unidades_del_grupo(representativo):
    carrera = representativo.unidad_curricular.malla_curricular.carrera
    return Paralelo.objects.filter(
        periodo_de_nivelacion=representativo.periodo_de_nivelacion,
        jornada=representativo.jornada,
        nombre=representativo.nombre,
        unidad_curricular__malla_curricular__carrera=carrera,
    ).select_related("unidad_curricular", "docente_responsable__usuario_de_sistema").order_by("unidad_curricular__nombre")


@requiere_perfil(*ROLES_VISUALIZAN)
def listar_horarios_paralelo(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    representativo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    unidades_rows = list(_unidades_del_grupo(representativo))

    unidades = []
    todas_completas = True
    for row in unidades_rows:
        agendadas = servicio_horas_agendadas_paralelo(row)
        requeridas = _horas_sincronicas_semanales(row.unidad_curricular, row.periodo_de_nivelacion)
        completo = agendadas >= requeridas
        todas_completas = todas_completas and completo
        unidades.append({
            "id": row.id,
            "nombre": row.unidad_curricular.nombre,
            "docente": row.docente_responsable,
            "agendadas": agendadas,
            "requeridas": requeridas,
            "restantes": round(max(requeridas - agendadas, 0), 2),
            "completo": completo,
        })

    horarios = Horario.objects.filter(paralelo__in=unidades_rows).select_related(
        "paralelo__unidad_curricular"
    ).order_by("paralelo__unidad_curricular__nombre", "dia_semana", "hora_inicio")

    jornada_enum = Jornada(representativo.jornada)

    # Construir datos de la grilla visual (Día × Hora)
    from poo.clases.franja_horaria import obtener_franja
    franja = obtener_franja(jornada_enum)
    slots_hora = []
    if franja:
        h = franja[0].hour
        while h < franja[1].hour:
            slots_hora.append(h)
            h += 1

    # Asignar colores en escalas de gris por unidad
    _COLORES_UNIDAD = [
        "#e8e8ed", "#d2d2d7", "#c7c7cc", "#b0b0b5", "#9a9a9f",
        "#aeaeb2", "#dcdce0", "#c4c4c8", "#bababe", "#8e8e93",
    ]
    nombres_unidades = sorted(set(h.paralelo.unidad_curricular.nombre for h in horarios))
    mapa_colores = {nombre: _COLORES_UNIDAD[i % len(_COLORES_UNIDAD)] for i, nombre in enumerate(nombres_unidades)}

    dias_semana = [d.value for d in DiaDeSemana]  # Lunes a Domingo (7 días)
    grilla = []  # lista de {hora, celdas: [{bloque o None} por día]}
    for slot in slots_hora:
        fila = {"hora": f"{slot:02d}:00", "celdas": []}
        for dia in dias_semana:
            bloque = None
            for h in horarios:
                if h.dia_semana == dia and h.hora_inicio.hour <= slot < h.hora_fin.hour:
                    bloque = {
                        "nombre": h.paralelo.unidad_curricular.nombre,
                        "hora_inicio": h.hora_inicio.strftime("%H:%M"),
                        "hora_fin": h.hora_fin.strftime("%H:%M"),
                        "slot_inicio": f"{slot:02d}:00",
                        "slot_fin": f"{slot+1:02d}:00",
                        "color": mapa_colores.get(h.paralelo.unidad_curricular.nombre, "#e8e8ed"),
                    }
                    break
            fila["celdas"].append(bloque)
        grilla.append(fila)

    return render(request, "academico/horarios_paralelo.html", {
        "representativo": representativo,
        "unidades": unidades,
        "horarios": horarios,
        "todas_completas": todas_completas,
        "es_planificacion": periodo_en_planificacion(representativo.periodo_de_nivelacion),
        "franja": texto_franja(jornada_enum),
        "dias": [dia.value for dia in DiaDeSemana],
        "dias_semana": dias_semana,
        "grilla": grilla,
        "mapa_colores": mapa_colores,
        "solo_lectura": usuario_es_solo_lectura(request.user),
        "titulo_pagina": "Horario - NIVEC",
        "titulo": f"Horarios - {representativo.nombre} ({representativo.unidad_curricular.malla_curricular.carrera.nombre})",
    })

@requiere_perfil(*ROLES_MODIFICAN)
def registrar_horario(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    representativo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    if request.method == "POST":
        unidad_id = request.POST.get("unidad_paralelo") or None
        fila = _unidades_del_grupo(representativo).filter(id=unidad_id).first() if unidad_id else None
        if not fila:
            messages.error(request, "Especifique una Unidad curricular válida")
            return redirect("listar_horarios_paralelo", paralelo_id=representativo.id)

        dia_semana = request.POST.get("dia_semana")
        tipo_de_sesion = "Sincrónica"
        espacio = (request.POST.get("espacio_de_imparticion") or "").strip()
        hora_inicio = _parsear_hora(request.POST.get("hora_inicio"))
        hora_fin = _parsear_hora(request.POST.get("hora_fin"))

        if not hora_inicio or not hora_fin:
            messages.error(request, "Las horas de inicio y finalización son requeridas")
            return redirect("listar_horarios_paralelo", paralelo_id=representativo.id)

        ok, mensaje = servicio_registrar_horario(
            fila, dia_semana, hora_inicio, hora_fin, espacio, tipo_de_sesion
        )
        (messages.success if ok else messages.error)(request, mensaje)

    return redirect("listar_horarios_paralelo", paralelo_id=representativo.id)

@requiere_perfil(*ROLES_MODIFICAN)
def editar_horario(request, horario_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    horario = get_object_or_404(
        Horario, id=horario_id,
        paralelo__periodo_de_nivelacion__universidad=universidad_usuario,
    )
    paralelo = horario.paralelo

    if request.method == "POST":
        dia_semana = request.POST.get("dia_semana")
        tipo_de_sesion = "Sincrónica"
        espacio = (request.POST.get("espacio_de_imparticion") or "").strip()
        hora_inicio = _parsear_hora(request.POST.get("hora_inicio"))
        hora_fin = _parsear_hora(request.POST.get("hora_fin"))

        if not hora_inicio or not hora_fin:
            messages.error(request, "Las horas de inicio y finalización son requeridas")
            return redirect("editar_horario", horario_id=horario.id)

        ok, mensaje = servicio_editar_horario(
            horario, dia_semana, hora_inicio, hora_fin, espacio, tipo_de_sesion
        )
        if ok:
            messages.success(request, mensaje)
            return redirect("listar_horarios_paralelo", paralelo_id=paralelo.id)
        messages.error(request, mensaje)

    jornada_enum = Jornada(paralelo.jornada)
    return render(request, "academico/editar_horario.html", {
        "horario": horario,
        "paralelo": paralelo,
        "franja": texto_franja(jornada_enum),
        "dias": [dia.value for dia in DiaDeSemana],
        "titulo_pagina": "Horario - NIVEC",
        "titulo": f"Editar sesión - {paralelo.unidad_curricular.nombre}",
    })

@requiere_perfil(*ROLES_MODIFICAN)
def generar_horario_sugerido(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    representativo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    if request.method == "POST":
        ok, mensaje = servicio_generar_horario_sugerido(representativo)
        (messages.success if ok else messages.error)(request, mensaje)

    return redirect("listar_horarios_paralelo", paralelo_id=representativo.id)

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