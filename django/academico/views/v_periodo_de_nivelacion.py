from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import ProtectedError

from academico.models import PeriodoDeNivelacion
from academico.forms import FormularioPeriodoDeNivelacion
from academico import services

from usuarios.utils import generar_identificador_siguiente, requiere_perfil, usuario_es_solo_lectura, ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR, ROL_COORDINADOR_DAN, ROL_COORDINADOR_UA

@requiere_perfil(ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR, ROL_COORDINADOR_DAN, ROL_COORDINADOR_UA)
def listar_periodos(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    periodos = PeriodoDeNivelacion.objects.filter(universidad=universidad_usuario).order_by("codigo_periodo")

    from usuarios.utils import obtener_rol_usuario
    rol = obtener_rol_usuario(request.user)
    solo_lectura = rol in (ROL_RECTOR, ROL_VICERRECTOR, ROL_COORDINADOR_DAN, ROL_COORDINADOR_UA)

    from academico.permisos import obtener_permisos_periodo
    permisos = obtener_permisos_periodo(universidad_usuario)

    return render(request, "academico/listar_periodos.html", {
        "periodos": periodos,
        "titulo_pagina": "Periodo de nivelación - NIVEC",
        "titulo": "Periodos de nivelación",
        "url_registrar": "registrar_periodo" if permisos["puede_registrar_periodo"] and not solo_lectura else None,
        "texto_registrar": "Registrar",
        "url_volver": "panel_principal",
        "solo_lectura": solo_lectura,
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def registrar_periodo(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente.")
        return redirect("panel_principal")

    if request.method == "POST":
        formulario = FormularioPeriodoDeNivelacion(request.POST, universidad=universidad_usuario)
        if formulario.is_valid():
            nuevo_periodo = formulario.save(commit=False)
            nuevo_periodo.universidad = universidad_usuario
            nuevo_periodo.codigo_periodo = generar_identificador_siguiente(PeriodoDeNivelacion, 'PNV', 'codigo_periodo')
            nuevo_periodo.anio = nuevo_periodo.fecha_inicio.year
            nuevo_periodo.periodo = f"{nuevo_periodo.anio}-{nuevo_periodo.numero_periodo}"
            # Calculate fecha_fin from fecha_inicio + semanas
            from datetime import timedelta
            nuevo_periodo.fecha_fin = nuevo_periodo.fecha_inicio + timedelta(days=nuevo_periodo.numero_de_semanas * 7)
            nuevo_periodo.save()
            
            messages.success(request, "El Periodo de nivelación ha sido registrado correctamente")
            return redirect("listar_periodos")
    else:
        formulario = FormularioPeriodoDeNivelacion(universidad=universidad_usuario)
        
    return render(request, "academico/formulario_periodo.html", {
        "formulario": formulario,
        "titulo_pagina": "Periodo de nivelación - NIVEC",
        "titulo": "Registrar Periodo de nivelación",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_periodos",
        "mostrar_carga_masiva": False,
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def modificar_periodo(request, periodo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    periodo = get_object_or_404(PeriodoDeNivelacion, id=periodo_id, universidad=universidad_usuario)

    if request.method == "POST":
        formulario = FormularioPeriodoDeNivelacion(request.POST, instance=periodo, universidad=universidad_usuario)
        if formulario.is_valid():
            periodo_modificado = formulario.save(commit=False)
            periodo_modificado.anio = periodo_modificado.fecha_inicio.year
            periodo_modificado.periodo = f"{periodo_modificado.anio}-{periodo_modificado.numero_periodo}"
            from datetime import timedelta
            periodo_modificado.fecha_fin = periodo_modificado.fecha_inicio + timedelta(days=periodo_modificado.numero_de_semanas * 7)
            periodo_modificado.save()
            messages.success(request, "El Periodo de nivelación ha sido modificado correctamente")
            return redirect("listar_periodos")
    else:
        formulario = FormularioPeriodoDeNivelacion(instance=periodo, universidad=universidad_usuario)
        
    return render(request, "academico/formulario_periodo.html", {
        "formulario": formulario,
        "titulo_pagina": "Periodo de nivelación - NIVEC",
        "titulo": "Modificar Periodo de nivelación", 
        "boton_texto": "Modificar",
        "url_cancelar": "listar_periodos",
        "mostrar_carga_masiva": False,
        "periodo": periodo
    })
    
@requiere_perfil(ROL_DIRECTOR_DAN)
def eliminar_periodo(request, periodo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    periodo = get_object_or_404(PeriodoDeNivelacion, id=periodo_id, universidad=universidad_usuario)
    try:
        periodo.delete()
        messages.success(request, "El Periodo de nivelación ha sido eliminado correctamente")
    except ProtectedError:
        messages.error(
            request,
            "No ha podido eliminar el Periodo de nivelación (registros asociados)"
        )
    return redirect("listar_periodos")

@requiere_perfil(ROL_DIRECTOR_DAN)
def iniciar_periodo(request, periodo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    periodo_db = get_object_or_404(PeriodoDeNivelacion, pk=periodo_id, universidad=universidad_usuario)
    if services.servicio_iniciar_periodo_de_nivelacion(periodo_db):
        messages.success(request, f"El Periodo de nivelación {periodo_db.periodo} ha iniciado")
    else:
        messages.error(request, "No se ha podido iniciar el Periodo de nivelación (Periodo de nivelación activo)")
        
    return redirect("listar_periodos")

@requiere_perfil(ROL_DIRECTOR_DAN)
def finalizar_periodo(request, periodo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    periodo_db = get_object_or_404(PeriodoDeNivelacion, pk=periodo_id, universidad=universidad_usuario)
    resultado = services.servicio_finalizar_periodo_de_nivelacion(periodo_db)
    if isinstance(resultado, tuple):
        ok, mensaje = resultado
        (messages.success if ok else messages.error)(request, mensaje)
    elif resultado:
        messages.success(request, f"El Periodo de nivelación {periodo_db.periodo} ha finalizado")
    else:
        messages.error(request, "No se ha podido finalizar el Periodo de nivelación")
        
    return redirect("listar_periodos")



@requiere_perfil(ROL_DIRECTOR_DAN)
def pasar_a_evaluacion(request, periodo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    periodo_db = get_object_or_404(PeriodoDeNivelacion, pk=periodo_id, universidad=universidad_usuario)
    if services.servicio_pasar_a_evaluacion(periodo_db):
        messages.success(request, f"El Periodo de nivelación {periodo_db.periodo} ha pasado a evaluación")
    else:
        messages.error(request, "No se ha podido pasar el Periodo de nivelación a evaluación")
    return redirect("listar_periodos")
