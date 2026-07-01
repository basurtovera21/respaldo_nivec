from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import ProtectedError, Count

from academico.models import Paralelo, PeriodoDeNivelacion, MatriculaParalelo
from academico.services import servicio_generar_paralelos, servicio_mover_estudiante, servicio_recalcular_cohorte_de_carrera, servicio_retirar_estudiante_de_paralelo, servicio_agregar_estudiante_a_paralelo, periodo_permite_gestion_matriculas
from usuarios.models import PerfilEstudiante
from poo.clases.enums.estado_de_periodo import EstadoDePeriodo
from poo.clases.enums.estado_de_matricula import EstadoDeMatricula
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


def _numero_para_orden(nombre):
    try:
        return int(str(nombre).split()[-1])
    except (ValueError, IndexError):
        return 0


def _paralelos_del_grupo(representativo):
    carrera = representativo.unidad_curricular.malla_curricular.carrera
    return Paralelo.objects.filter(
        periodo_de_nivelacion=representativo.periodo_de_nivelacion,
        jornada=representativo.jornada,
        nombre=representativo.nombre,
        unidad_curricular__malla_curricular__carrera=carrera,
    )

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
        "unidad_curricular__malla_curricular__carrera",
    ).annotate(_n_estudiantes=Count("estudiantes_matriculados"))

    periodo_id = request.GET.get("periodo")
    periodo_seleccionado = None
    if periodo_id:
        paralelos = paralelos.filter(periodo_de_nivelacion__id=periodo_id)
        periodo_seleccionado = periodos.filter(id=periodo_id).first()

    grupos = {}
    for p in paralelos:
        carrera = p.unidad_curricular.malla_curricular.carrera
        clave = (p.periodo_de_nivelacion_id, carrera.id, p.jornada, p.nombre)
        if clave not in grupos:
            grupos[clave] = {
                "representativo_id": p.id,
                "codigo": p.codigo_de_paralelo,
                "nombre": p.nombre,
                "carrera": carrera.nombre,
                "periodo": p.periodo_de_nivelacion.periodo,
                "jornada": p.get_jornada_display(),
                "modalidad": p.get_modalidad_display(),
                "capacidad": p.capacidad_maxima,
                "unidades": 0,
                "estudiantes": p._n_estudiantes,
                "_orden": (carrera.nombre, _numero_para_orden(p.nombre)),
            }
        grupos[clave]["unidades"] += 1

    paralelos_agrupados = sorted(grupos.values(), key=lambda g: g["_orden"])

    return render(request, "academico/listar_paralelos.html", {
        "paralelos": paralelos_agrupados,
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
                f"{resumen['grupos_creados']} Paralelos creados. {resumen['estudiantes_distribuidos']} Estudiantes distribuidos"
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
        "titulo": "Crear Paralelos",
        "url_cancelar": "listar_paralelos",
    })

@requiere_perfil(*ROLES_MODIFICAN)
def eliminar_paralelo(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    representativo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    periodo = representativo.periodo_de_nivelacion
    carrera = representativo.unidad_curricular.malla_curricular.carrera
    paralelos_grupo = _paralelos_del_grupo(representativo)

    with transaction.atomic():
        MatriculaParalelo.objects.filter(paralelo__in=paralelos_grupo).delete()
        paralelos_grupo.delete()

    servicio_recalcular_cohorte_de_carrera(periodo, carrera)

    messages.success(request, f"El Paralelo ha sido eliminado correctamente")
    return redirect("listar_paralelos")

@requiere_perfil(*ROLES_VISUALIZAN)
def detalle_paralelo(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    representativo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )
    carrera = representativo.unidad_curricular.malla_curricular.carrera

    unidades = _paralelos_del_grupo(representativo).select_related(
        "unidad_curricular",
        "docente_responsable__usuario_de_sistema",
    ).order_by("unidad_curricular__nombre")

    return render(request, "academico/detalle_paralelo.html", {
        "representativo": representativo,
        "carrera": carrera,
        "unidades": unidades,
        "solo_lectura": usuario_es_solo_lectura(request.user),
        "titulo_pagina": "Paralelo - NIVEC",
        "titulo": f"{representativo.nombre} - {carrera.nombre} ({representativo.get_jornada_display()})",
    })

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

    periodo = paralelo.periodo_de_nivelacion
    ocupacion = matriculas.count()
    capacidad = paralelo.capacidad_maxima
    puede_gestionar = periodo_permite_gestion_matriculas(periodo)

    otros = Paralelo.objects.filter(
        periodo_de_nivelacion=paralelo.periodo_de_nivelacion,
        jornada=paralelo.jornada,
        unidad_curricular__malla_curricular__carrera=carrera,
    ).exclude(nombre=paralelo.nombre).annotate(_n_estudiantes=Count("estudiantes_matriculados"))

    representativos = {}
    for otro in otros:
        if otro.nombre not in representativos:
            representativos[otro.nombre] = otro

    destinos = []
    for nombre_grupo in sorted(representativos.keys()):
        rep = representativos[nombre_grupo]
        ocupacion_destino = rep._n_estudiantes
        destinos.append({
            "nombre": nombre_grupo,
            "paralelo_id": rep.id,
            "ocupacion": ocupacion_destino,
            "capacidad": rep.capacidad_maxima,
            "lleno": ocupacion_destino >= rep.capacidad_maxima,
        })

    return render(request, "academico/estudiantes_paralelo.html", {
        "paralelo": paralelo,
        "matriculas": matriculas,
        "destinos": destinos,
        "puede_gestionar": puede_gestionar,
        "ocupacion": ocupacion,
        "capacidad": capacidad,
        "lleno": ocupacion >= capacidad,
        "solo_lectura": usuario_es_solo_lectura(request.user),
        "titulo_pagina": "Paralelo - NIVEC",
        "titulo": f"{paralelo.nombre} ({paralelo.unidad_curricular.nombre})",
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
            messages.error(request, "Especifique un Estudiante y un Paralelo de destino")
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


@requiere_perfil(*ROLES_MODIFICAN)
def retirar_estudiante(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    if request.method == "POST":
        estudiante_id = request.POST.get("estudiante") or None
        if not estudiante_id:
            messages.error(request, "Especifique un Estudiante")
            return redirect("listar_estudiantes_paralelo", paralelo_id=paralelo.id)

        estudiante = get_object_or_404(
            PerfilEstudiante,
            id=estudiante_id,
            carrera_registrada__campus__universidad=universidad_usuario,
        )
        ok, mensaje = servicio_retirar_estudiante_de_paralelo(estudiante, paralelo)
        (messages.success if ok else messages.error)(request, mensaje)

    return redirect("listar_estudiantes_paralelo", paralelo_id=paralelo.id)


@requiere_perfil(*ROLES_MODIFICAN)
def estudiantes_disponibles(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )
    carrera = paralelo.unidad_curricular.malla_curricular.carrera
    periodo = paralelo.periodo_de_nivelacion

    if not periodo_permite_gestion_matriculas(periodo):
        messages.warning(request, "Solo se puede gestionar la matrícula en Periodos en planificación o en curso")
        return redirect("listar_estudiantes_paralelo", paralelo_id=paralelo.id)

    ocupacion = MatriculaParalelo.objects.filter(paralelo=paralelo).count()
    capacidad = paralelo.capacidad_maxima

    no_asignados = PerfilEstudiante.objects.filter(
        carrera_registrada=carrera,
        jornada=paralelo.jornada,
        periodo_de_nivelacion=periodo,
        estado_de_matricula=EstadoDeMatricula.MATRICULADO.value,
    ).exclude(
        estudiantes_matriculados__paralelo__periodo_de_nivelacion=periodo
    ).distinct().select_related("usuario_de_sistema").order_by(
        "usuario_de_sistema__apellidos", "usuario_de_sistema__nombres"
    )

    return render(request, "academico/estudiantes_disponibles.html", {
        "paralelo": paralelo,
        "no_asignados": no_asignados,
        "ocupacion": ocupacion,
        "capacidad": capacidad,
        "lleno": ocupacion >= capacidad,
        "titulo_pagina": "Paralelo - NIVEC",
        "titulo": f"Agregar estudiante - {paralelo.nombre}",
    })


@requiere_perfil(*ROLES_MODIFICAN)
def agregar_estudiante(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    if request.method == "POST":
        estudiante_id = request.POST.get("estudiante") or None
        if not estudiante_id:
            messages.error(request, "Especifique un Estudiante")
            return redirect("estudiantes_disponibles", paralelo_id=paralelo.id)

        estudiante = get_object_or_404(
            PerfilEstudiante,
            id=estudiante_id,
            carrera_registrada__campus__universidad=universidad_usuario,
        )
        ok, mensaje = servicio_agregar_estudiante_a_paralelo(estudiante, paralelo)
        (messages.success if ok else messages.error)(request, mensaje)

    return redirect("estudiantes_disponibles", paralelo_id=paralelo.id)