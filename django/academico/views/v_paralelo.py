from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import ProtectedError

from academico.models import Paralelo, PeriodoDeNivelacion, MatriculaParalelo
from academico.services import servicio_generar_paralelos, servicio_mover_estudiante
from usuarios.models import PerfilEstudiante
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

@requiere_perfil(*ROLES_VISUALIZAN)
def listar_paralelos(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    periodos = PeriodoDeNivelacion.objects.filter(universidad=universidad_usuario)

    paralelos = Paralelo.objects.filter(
        periodo_de_nivelacion__universidad=universidad_usuario
    ).select_related(
        "periodo_de_nivelacion",
        "unidad_curricular",
        "unidad_curricular__malla_curricular__carrera",
        "docente_responsable__usuario_de_sistema",
    )

    periodo_id = request.GET.get("periodo")
    periodo_seleccionado = None
    if periodo_id:
        paralelos = paralelos.filter(periodo_de_nivelacion__id=periodo_id)
        periodo_seleccionado = periodos.filter(id=periodo_id).first()

    return render(request, "academico/listar_paralelos.html", {
        "paralelos": paralelos,
        "periodos": periodos,
        "periodo_seleccionado": periodo_seleccionado,
        "solo_lectura": usuario_es_solo_lectura(request.user),
        "titulo_pagina": "Paralelo - NIVEC",
        "titulo": "Paralelos",
        "url_volver": "panel_dan",
    })

@requiere_perfil(*ROLES_MODIFICAN)
def generar_paralelos(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    periodos = PeriodoDeNivelacion.objects.filter(
        universidad=universidad_usuario,
        estado=EstadoDePeriodo.PLANIFICACION.value,
    )

    if not periodos.exists():
        messages.warning(request, "No existen Periodos de nivelación en planificación")
        return redirect("panel_dan")

    if request.method == "POST":
        periodo_id = request.POST.get("periodo") or None
        periodo = periodos.filter(id=periodo_id).first() if periodo_id else None
        if not periodo:
            messages.error(request, "Especifique un Periodo de nivelación en planificación")
            return redirect("generar_paralelos")


        capacidad = request.POST.get("capacidad") or 35

        resumen = servicio_generar_paralelos(periodo, capacidad)

        for advertencia in resumen["advertencias"]:
            messages.warning(request, advertencia)

        if resumen["paralelos_creados"] > 0 or resumen["estudiantes_distribuidos"] > 0:
            messages.success(
                request,
                f"{resumen['grupos_creados']} Paralelo(s) creado(s). {resumen['estudiantes_distribuidos']} Estudiante(s) distribuido(s)."
            )
        else:
            messages.warning(
                request,
                "No quedan Estudiantes pendientes por distribuir actualmente"
            )

        return redirect("listar_paralelos")

    return render(request, "academico/generar_paralelos.html", {
        "periodos": periodos,
        "titulo_pagina": "Paralelo - NIVEC",
        "titulo": "Crear paralelos",
        "url_cancelar": "listar_paralelos",
    })

@requiere_perfil(*ROLES_MODIFICAN)
def eliminar_paralelo(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    try:
        paralelo.delete()
        messages.success(request, "El Paralelo ha sido eliminado correctamente")
    except ProtectedError:
        total = paralelo.estudiantes_matriculados.count()
        messages.error(
            request,
            f"El Paralelo no se ha podido eliminar ({total} Estudiante(s) matriculado(s))"
        )
    return redirect("listar_paralelos")

@requiere_perfil(*ROLES_VISUALIZAN)
def listar_estudiantes_paralelo(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )
    carrera = paralelo.unidad_curricular.malla_curricular.carrera

    matriculas = MatriculaParalelo.objects.filter(
        paralelo=paralelo
    ).select_related("estudiante__usuario_de_sistema")

    otros = Paralelo.objects.filter(
        periodo_de_nivelacion=paralelo.periodo_de_nivelacion,
        jornada=paralelo.jornada,
        unidad_curricular__malla_curricular__carrera=carrera,
    ).exclude(nombre=paralelo.nombre)

    representativos = {}
    for otro in otros:
        if otro.nombre not in representativos:
            representativos[otro.nombre] = otro

    destinos = []
    for nombre_grupo in sorted(representativos.keys()):
        rep = representativos[nombre_grupo]
        ocupacion = MatriculaParalelo.objects.filter(paralelo=rep).count()
        destinos.append({
            "nombre": nombre_grupo,
            "paralelo_id": rep.id,
            "ocupacion": ocupacion,
            "capacidad": rep.capacidad_maxima,
            "lleno": ocupacion >= rep.capacidad_maxima,
        })

    return render(request, "academico/estudiantes_paralelo.html", {
        "paralelo": paralelo,
        "matriculas": matriculas,
        "destinos": destinos,
        "solo_lectura": usuario_es_solo_lectura(request.user),
        "titulo_pagina": "Paralelo - NIVEC",
        "titulo": f"Estudiantes - {paralelo.nombre} ({paralelo.unidad_curricular.nombre})",
    })

@requiere_perfil(*ROLES_MODIFICAN)
def mover_estudiante(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    if request.method == "POST":
        estudiante_id = request.POST.get("estudiante") or None
        destino_id = request.POST.get("paralelo_destino") or None

        if not estudiante_id or not destino_id:
            messages.error(request, "Especifique un Estudiante y un Paralelo destino")
            return redirect("listar_estudiantes_paralelo", paralelo_id=paralelo.id)

        estudiante = get_object_or_404(
            PerfilEstudiante,
            id=estudiante_id,
            carrera_registrada__campus__universidad=universidad_usuario,
        )
        paralelo_destino = get_object_or_404(
            Paralelo,
            id=destino_id,
            periodo_de_nivelacion__universidad=universidad_usuario,
        )

        ok, mensaje = servicio_mover_estudiante(estudiante, paralelo_destino)
        if ok:
            messages.success(request, mensaje)
        else:
            messages.error(request, mensaje)

    return redirect("listar_estudiantes_paralelo", paralelo_id=paralelo.id)