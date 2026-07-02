from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import ProtectedError
from django.http import HttpResponse
import openpyxl

from academico.models import UnidadCurricular, MallaCurricular, Carrera
from academico.forms import FormularioUnidadCurricular
from academico.services import (
    servicio_unidad_registrar_masivo_desde_excel,
    servicio_recalcular_total_horas_malla,
)
from poo.clases.enums.estado_de_malla import EstadoDeMalla
from usuarios.utils import (
    generar_identificador_siguiente,
    requiere_perfil,
    usuario_es_solo_lectura,
    ROL_COORDINADOR_DAN,
    ROL_DIRECTOR_DAN,
    ROL_RECTOR,
    ROL_VICERRECTOR,
)

ROLES_VISUALIZAN = (ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR)
ROLES_MODIFICAN = (ROL_COORDINADOR_DAN, ROL_DIRECTOR_DAN)
ESTADOS_MALLA_EDITABLE = [EstadoDeMalla.DISENO.value, EstadoDeMalla.ACTIVA.value]

@requiere_perfil(*ROLES_VISUALIZAN)
def listar_unidades(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    carrera_id = request.GET.get("carrera")
    carreras = Carrera.objects.filter(
        campus__universidad=universidad_usuario,
        mallas_curriculares__isnull=False,
    ).distinct()

    unidades = UnidadCurricular.objects.filter(
        malla_curricular__carrera__campus__universidad=universidad_usuario
    ).select_related("malla_curricular__carrera")

    if carrera_id:
        unidades = unidades.filter(malla_curricular__carrera__id=carrera_id)

    carrera_seleccionada = None
    if carrera_id:
        carrera_seleccionada = carreras.filter(id=carrera_id).first()

    return render(request, "academico/listar_unidades.html", {
        "solo_lectura": usuario_es_solo_lectura(request.user),
        "unidades": unidades,
        "carreras": carreras,
        "carrera_seleccionada": carrera_seleccionada,
        "titulo_pagina": "Unidad curricular - NIVEC",
        "titulo": "Unidades curriculares",
        "url_registrar": "registrar_unidad",
        "texto_registrar": "Registrar",
        "url_volver": "panel_dan"
    })

@requiere_perfil(*ROLES_VISUALIZAN)
def listar_unidades_de_malla(request, malla_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    malla = get_object_or_404(
        MallaCurricular, id=malla_id, carrera__campus__universidad=universidad_usuario
    )

    unidades = UnidadCurricular.objects.filter(
        malla_curricular=malla
    ).select_related("malla_curricular")

    return render(request, "academico/listar_unidades.html", {
        "solo_lectura": usuario_es_solo_lectura(request.user),
        "unidades": unidades,
        "malla": malla,
        "titulo_pagina": "Unidad curricular - NIVEC",
        "titulo": f"Unidades curriculares ({malla.nombre})",
        "url_registrar": "registrar_unidad",
        "texto_registrar": "Registrar",
        "url_volver": "listar_mallas"
    })

@requiere_perfil(*ROLES_MODIFICAN)
def descargar_plantilla_unidad(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Unidades curriculares"

    cabeceras = [
        "Código de malla (MC...)",
        "Nombre de la Unidad curricular",
        "Horas totales (número decimal)",
        "Horas sincrónicas (número decimal)",
        "Horas sincrónicas semanales (número entero)",
        "Horas asincrónicas (número decimal)",
        "Criterio de aprobación (0.0 - 10.0)",
        "Porcentaje mínimo de asistencia (0.0 - 100.0)",
    ]
    ws.append(cabeceras)

    for col in range(1, len(cabeceras) + 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 40

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="formato_unidades_nivec.xlsx"'
    wb.save(response)
    return response

@requiere_perfil(*ROLES_MODIFICAN)
def registrar_unidad(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    mallas_existentes = MallaCurricular.objects.filter(
        carrera__campus__universidad=universidad_usuario,
        estado__in=ESTADOS_MALLA_EDITABLE,
    )
    if not mallas_existentes.exists():
        messages.warning(
            request,
            "No existen registros de Mallas curriculares (diseño o activa) actualmente"
        )
        return redirect("listar_mallas")

    malla_id = request.GET.get("malla")
    malla_contexto = mallas_existentes.filter(id=malla_id).first() if malla_id else None

    if request.method == "POST":
        if "archivo_excel" in request.FILES:
            archivo = request.FILES["archivo_excel"]
            if not archivo.name.endswith(".xlsx"):
                messages.error(request, "Documento con formato no válido")
                return redirect("registrar_unidad")

            resultado = servicio_unidad_registrar_masivo_desde_excel(archivo, universidad_usuario)

            if resultado["error"]:
                messages.error(request, resultado["error"])
            for adv in resultado["advertencias"]:
                messages.warning(request, adv)
            if resultado["exitosos"] > 0:
                for malla in MallaCurricular.objects.filter(
                    carrera__campus__universidad=universidad_usuario
                ):
                    servicio_recalcular_total_horas_malla(malla)
                messages.success(
                    request,
                    f"{resultado['exitosos']} Unidades curriculares registradas correctamente"
                )
            return redirect("listar_unidades")

        else:
            formulario = FormularioUnidadCurricular(request.POST)
            formulario.fields["malla_curricular"].queryset = mallas_existentes

            if formulario.is_valid():
                nueva_unidad = formulario.save(commit=False)
                nueva_unidad.codigo_de_unidad = generar_identificador_siguiente(
                    UnidadCurricular, "UC", "codigo_de_unidad"
                )
                nueva_unidad.save()
                servicio_recalcular_total_horas_malla(nueva_unidad.malla_curricular)
                messages.success(
                    request, "La Unidad curricular ha sido registrada correctamente"
                )
                if malla_contexto:
                    return redirect("listar_unidades_de_malla", malla_id=malla_contexto.id)
                return redirect("listar_unidades")
    else:
        formulario = FormularioUnidadCurricular(
            initial={"malla_curricular": malla_contexto} if malla_contexto else None
        )
        formulario.fields["malla_curricular"].queryset = mallas_existentes

    return render(request, "academico/formulario_unidad.html", {
        "formulario": formulario,
        "titulo_pagina": "Unidad curricular - NIVEC",
        "titulo": "Registrar Unidad curricular",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_unidades",
        "mostrar_carga_masiva": True,
        "url_plantilla": "descargar_plantilla_unidad",
    })

@requiere_perfil(*ROLES_MODIFICAN)
def modificar_unidad(request, unidad_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    unidad = get_object_or_404(
        UnidadCurricular,
        id=unidad_id,
        malla_curricular__carrera__campus__universidad=universidad_usuario
    )

    if request.method == "POST":
        malla_anterior_id = unidad.malla_curricular_id
        formulario = FormularioUnidadCurricular(request.POST, instance=unidad)
        formulario.fields["malla_curricular"].queryset = MallaCurricular.objects.filter(
            carrera__campus__universidad=universidad_usuario,
            estado__in=ESTADOS_MALLA_EDITABLE,
        )
        if formulario.is_valid():
            unidad_modificada = formulario.save()
            servicio_recalcular_total_horas_malla(unidad_modificada.malla_curricular)
            if malla_anterior_id != unidad_modificada.malla_curricular_id:
                malla_anterior = MallaCurricular.objects.filter(id=malla_anterior_id).first()
                if malla_anterior:
                    servicio_recalcular_total_horas_malla(malla_anterior)
            messages.success(
                request, "La Unidad curricular ha sido modificada correctamente"
            )
            return redirect("listar_unidades")
    else:
        formulario = FormularioUnidadCurricular(instance=unidad)
        formulario.fields["malla_curricular"].queryset = MallaCurricular.objects.filter(
            carrera__campus__universidad=universidad_usuario,
             estado__in=ESTADOS_MALLA_EDITABLE,
        )

    return render(request, "academico/formulario_unidad.html", {
        "formulario": formulario,
        "titulo_pagina": "Unidad curricular - NIVEC",
        "titulo": "Modificar Unidad curricular",
        "boton_texto": "Modificar",
        "url_cancelar": "listar_unidades",
        "mostrar_carga_masiva": False,
    })

@requiere_perfil(*ROLES_MODIFICAN)
def eliminar_unidad(request, unidad_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    unidad = get_object_or_404(
        UnidadCurricular,
        id=unidad_id,
        malla_curricular__carrera__campus__universidad=universidad_usuario
    )
    malla = unidad.malla_curricular
    try:
        unidad.delete()
        servicio_recalcular_total_horas_malla(malla)
        messages.success(request, "La Unidad curricular ha sido eliminada correctamente")
    except ProtectedError:
        messages.error(
            request,
            "La Unidad curricular no se ha podido eliminar (registros presentes)"
        )
    return redirect("listar_unidades")