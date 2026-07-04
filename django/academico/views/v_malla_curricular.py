from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import ProtectedError
from django.http import HttpResponse
import openpyxl

from academico.models import MallaCurricular, Carrera
from academico.forms import FormularioMallaCurricular
from academico.services import (
    servicio_malla_registrar_masivo_desde_excel,
    servicio_clonar_malla_curricular,
    servicio_cambiar_estado_malla,
    servicio_generar_version_malla,
)

from usuarios.utils import (
    generar_identificador_siguiente,
    requiere_perfil,
    usuario_es_solo_lectura,
    ROL_COORDINADOR_DAN,
    ROL_DIRECTOR_DAN,
    ROL_RECTOR,
    ROL_VICERRECTOR,
    ROL_COORDINADOR_UA,
)

ROLES_VISUALIZAN = (ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR, ROL_COORDINADOR_UA)
ROLES_MODIFICAN = (ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN)

@requiere_perfil(*ROLES_VISUALIZAN)
def listar_mallas(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    mallas = MallaCurricular.objects.filter(
        carrera__campus__universidad=universidad_usuario
    ).select_related("carrera")

    from usuarios.utils import obtener_rol_usuario
    rol = obtener_rol_usuario(request.user)
    es_coordinador_ua = (rol == ROL_COORDINADOR_UA)
    solo_lectura = rol in (ROL_RECTOR, ROL_VICERRECTOR, ROL_COORDINADOR_UA)

    if es_coordinador_ua:
        perfil_admin = getattr(request.user, 'perfil_administrativo', None)
        if perfil_admin and perfil_admin.carrera_asignada:
            mallas = mallas.filter(carrera=perfil_admin.carrera_asignada)

    carreras_disponibles = Carrera.objects.filter(campus__universidad=universidad_usuario).order_by("nombre")
    carrera_filtro = request.GET.get("carrera", "")
    if carrera_filtro:
        mallas = mallas.filter(carrera_id=carrera_filtro)

    return render(request, "academico/listar_mallas.html", {
        "solo_lectura": solo_lectura,
        "es_coordinador_ua": es_coordinador_ua,
        "carreras_disponibles": carreras_disponibles,
        "carrera_filtro": carrera_filtro,
        "mallas": mallas,
        "titulo_pagina": "Malla curricular - NIVEC",
        "titulo": "Mallas curriculares",
        "url_registrar": "registrar_malla",
        "texto_registrar": "Registrar",
        "url_volver": "panel_principal"
    })

@requiere_perfil(*ROLES_MODIFICAN)
def descargar_plantilla_malla(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mallas curriculares"

    cabeceras = [
        "Código de Carrera (CAR...)",
        "Nombre de la Malla curricular",
    ]
    ws.append(cabeceras)

    for col in range(1, len(cabeceras) + 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 40

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="formato_mallas_nivec.xlsx"'
    wb.save(response)
    return response


@requiere_perfil(*ROLES_MODIFICAN)
def registrar_malla(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    carreras_existentes = Carrera.objects.filter(campus__universidad=universidad_usuario)
    if not carreras_existentes.exists():
        messages.warning(request, "No existen registros de Carrera actualmente")
        return redirect("panel_dan")

    if request.method == "POST":
        if "archivo_excel" in request.FILES:
            archivo = request.FILES["archivo_excel"]
            if not archivo.name.endswith(".xlsx"):
                messages.error(request, "Documento con formato no válido")
                return redirect("registrar_malla")

            resultado = servicio_malla_registrar_masivo_desde_excel(archivo, universidad_usuario)

            if resultado["error"]:
                messages.error(request, resultado["error"])
            for adv in resultado["advertencias"]:
                messages.warning(request, adv)
            if resultado["exitosos"] > 0:
                messages.success(
                    request,
                    f"{resultado['exitosos']} Mallas curriculares registradas correctamente"
                )
            return redirect("listar_mallas")

        else:
            formulario = FormularioMallaCurricular(request.POST)
            formulario.fields["carrera"].queryset = carreras_existentes

            if formulario.is_valid():
                nueva_malla = formulario.save(commit=False)
                nueva_malla.codigo_de_malla = generar_identificador_siguiente(
                    MallaCurricular, "MC", "codigo_de_malla"
                )
                nueva_malla.version_de_malla = servicio_generar_version_malla(nueva_malla.carrera)
                nueva_malla.save()
                messages.success(request, "La Malla curricular ha sido registrada correctamente")
                return redirect("listar_mallas")
    else:
        formulario = FormularioMallaCurricular()
        formulario.fields["carrera"].queryset = carreras_existentes

    return render(request, "academico/formulario_malla.html", {
        "formulario": formulario,
        "titulo_pagina": "Malla curricular - NIVEC",
        "titulo": "Registrar Malla curricular",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_mallas",
        "mostrar_carga_masiva": True,
        "url_plantilla": "descargar_plantilla_malla",
    })


@requiere_perfil(*ROLES_MODIFICAN)
def modificar_malla(request, malla_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    malla = get_object_or_404(
        MallaCurricular, id=malla_id, carrera__campus__universidad=universidad_usuario
    )

    if request.method == "POST":
        formulario = FormularioMallaCurricular(request.POST, instance=malla)
        formulario.fields["carrera"].queryset = Carrera.objects.filter(
            campus__universidad=universidad_usuario
        )
        formulario.fields['carrera'].disabled = True
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "La Malla curricular ha sido modificada correctamente")
            return redirect("listar_mallas")
    else:
        formulario = FormularioMallaCurricular(instance=malla)
        formulario.fields["carrera"].queryset = Carrera.objects.filter(
            campus__universidad=universidad_usuario
        )
        formulario.fields['carrera'].disabled = True

    return render(request, "academico/formulario_malla.html", {
        "formulario": formulario,
        "titulo_pagina": "Malla curricular - NIVEC",
        "titulo": "Modificar Malla curricular",
        "boton_texto": "Modificar",
        "url_cancelar": "listar_mallas",
        "mostrar_carga_masiva": False,
    })

@requiere_perfil(*ROLES_MODIFICAN)
def eliminar_malla(request, malla_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    malla = get_object_or_404(
        MallaCurricular, id=malla_id, carrera__campus__universidad=universidad_usuario
    )

    try:
        malla.delete()
        messages.success(request, "La Malla curricular ha sido eliminada correctamente")
    except ProtectedError:
        total_unidades = malla.unidades_curriculares.count()
        messages.error(
            request,
            f"La Malla curricular no se ha podido eliminar (registros asociados)"
        )
    return redirect("listar_mallas")

@requiere_perfil(*ROLES_MODIFICAN)
def clonar_malla(request, malla_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    malla = get_object_or_404(
        MallaCurricular, id=malla_id, carrera__campus__universidad=universidad_usuario
    )

    if request.method == "POST":
        nuevo_nombre = (request.POST.get("nombre") or "").strip()

        nueva_malla = servicio_clonar_malla_curricular(malla.id, nuevo_nombre or None)
        total_unidades = nueva_malla.unidades_curriculares.count()
        messages.success(
            request,
            f"La Malla curricular fue copiada correctamente"
        )
        return redirect("listar_mallas")

    return render(request, "academico/formulario_clonar_malla.html", {
        "malla": malla,
        "titulo_pagina": "Malla curricular - NIVEC",
        "titulo": "Copiar Malla curricular",
        "boton_texto": "Copiar",
        "url_cancelar": "listar_mallas",
    })


@requiere_perfil(*ROLES_MODIFICAN)
def cambiar_estado_malla(request, malla_id, accion):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    malla = get_object_or_404(
        MallaCurricular, id=malla_id, carrera__campus__universidad=universidad_usuario
    )

    ok, mensaje = servicio_cambiar_estado_malla(malla, accion)
    if ok:
        messages.success(request, mensaje)
    else:
        messages.error(request, mensaje)
    return redirect("listar_mallas")