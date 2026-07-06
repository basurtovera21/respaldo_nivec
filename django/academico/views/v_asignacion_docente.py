from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from academico.models import Paralelo
from academico.services import (
    servicio_evaluar_docentes_para_paralelo,
    servicio_asignar_docente,
    servicio_quitar_docente,
)
from usuarios.utils import (
    requiere_perfil,
    usuario_es_solo_lectura,
    obtener_rol_usuario,
    ROL_COORDINADOR_DAN,
    ROL_DIRECTOR_DAN,
    ROL_RECTOR,
    ROL_VICERRECTOR,
    ROL_COORDINADOR_UA,
)

ROLES_VISUALIZAN = (ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR, ROL_COORDINADOR_UA)

@requiere_perfil(*ROLES_VISUALIZAN)
def asignar_docente_paralelo(request, paralelo_id):
    perfil_admin = getattr(request.user, 'perfil_administrativo', None)
    universidad_usuario = perfil_admin.universidad if perfil_admin else None
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo, id=paralelo_id, periodo_de_nivelacion__universidad=universidad_usuario
    )

    solo_lectura = usuario_es_solo_lectura(request.user)

    if request.method == "POST" and not solo_lectura:
        accion = request.POST.get("accion")
        if accion == "quitar":
            ok, mensaje = servicio_quitar_docente(paralelo)
            (messages.success if ok else messages.error)(request, mensaje)
        else:
            docente_id = request.POST.get("docente_id")
            if not docente_id:
                messages.error(request, "Especifique un Docente")
            else:
                from usuarios.models import PerfilDocente
                docente = get_object_or_404(
                    PerfilDocente, id=docente_id, universidad=universidad_usuario
                )
                ok, mensaje, advertencia = servicio_asignar_docente(paralelo, docente)
                if ok:
                    messages.success(request, mensaje)
                    if advertencia:
                        messages.warning(request, advertencia)
                else:
                    messages.error(request, mensaje)
        return redirect("asignar_docente_paralelo", paralelo_id=paralelo.id)

    evaluaciones = servicio_evaluar_docentes_para_paralelo(paralelo)

    from academico.models import Horario
    from academico.services import servicio_horas_agendadas_paralelo, _horas_sincronicas_semanales
    tiene_horario = Horario.objects.filter(paralelo=paralelo).exists()
    horas_agendadas = servicio_horas_agendadas_paralelo(paralelo)
    horas_requeridas = _horas_sincronicas_semanales(paralelo.unidad_curricular, paralelo.periodo_de_nivelacion)
    horario_completo = horas_agendadas >= horas_requeridas

    if not horario_completo:
        messages.warning(request, "El Horario de la Unidad curricular debe estar completado antes de designar un Docente")
        return redirect("detalle_paralelo", paralelo_id=paralelo.id)

    return render(request, "academico/asignar_docente.html", {
        "paralelo": paralelo,
        "evaluaciones": evaluaciones,
        "tiene_horario": tiene_horario,
        "horario_completo": horario_completo,
        "horas_semanales": horas_requeridas,
        "solo_lectura": solo_lectura,
        "titulo_pagina": "Docente - NIVEC",
        "titulo": f"Designación Docente - {paralelo.nombre} ({paralelo.unidad_curricular.nombre})",
    })