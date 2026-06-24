from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import openpyxl

from academico.models import UnidadCurricular, MallaCurricular, Carrera
from academico.forms import FormularioUnidadCurricular
from academico.services import servicio_unidad_registrar_masivo_desde_excel
from usuarios.utils import generar_identificador_siguiente


@login_required
def listar_unidades(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    carrera_id = request.GET.get("carrera")
    carreras = Carrera.objects.filter(campus__universidad=universidad_usuario)

    unidades = UnidadCurricular.objects.filter(
        malla_curricular__carrera__campus__universidad=universidad_usuario
    ).select_related("malla_curricular__carrera")

    if carrera_id:
        unidades = unidades.filter(malla_curricular__carrera__id=carrera_id)

    carrera_seleccionada = None
    if carrera_id:
        carrera_seleccionada = carreras.filter(id=carrera_id).first()

    return render(request, "academico/listar_unidades.html", {
        "unidades": unidades,
        "carreras": carreras,
        "carrera_seleccionada": carrera_seleccionada,
        "titulo_pagina": "Unidades curriculares - NIVEC",
        "titulo": "Unidades curriculares",
        "url_registrar": "registrar_unidad",
        "texto_registrar": "Registrar",
        "url_volver": "panel_dan"
    })


@login_required
def listar_unidades_de_malla(request, malla_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    malla = get_object_or_404(
        MallaCurricular, id=malla_id, carrera__campus__universidad=universidad_usuario
    )

    unidades = UnidadCurricular.objects.filter(
        malla_curricular=malla
    ).select_related("malla_curricular")

    return render(request, "academico/listar_unidades.html", {
        "unidades": unidades,
        "malla": malla,
        "titulo_pagina": "Unidades curriculares - NIVEC",
        "titulo": f"Unidades curriculares — {malla.nombre}",
        "url_registrar": "registrar_unidad",
        "texto_registrar": "Registrar",
        "url_volver": "listar_mallas"
    })


@login_required
def descargar_plantilla_unidad(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Unidades curriculares"

    cabeceras = [
        "Código de malla (MC...)",
        "Nombre de la unidad curricular",
        "Áreas de conocimiento (separadas por comas)",
        "Horas totales",
        "Horas semanales",
        "Horas sincrónicas",
        "Horas asincrónicas",
        "Tipo de componente (Teórico, Práctico, Tutorial)",
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


@login_required
def registrar_unidad(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    mallas_existentes = MallaCurricular.objects.filter(
        carrera__campus__universidad=universidad_usuario
    )
    if not mallas_existentes.exists():
        messages.warning(request, "No existen registros de mallas curriculares actualmente")
        return redirect("panel_dan")

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
                messages.success(
                    request,
                    f"{resultado['exitosos']} unidades curriculares registradas correctamente"
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
                messages.success(
                    request, "La unidad curricular ha sido registrada correctamente"
                )
                return redirect("listar_unidades")
    else:
        formulario = FormularioUnidadCurricular()
        formulario.fields["malla_curricular"].queryset = mallas_existentes

    return render(request, "academico/formulario_unidad.html", {
        "formulario": formulario,
        "titulo_pagina": "Unidades curriculares - NIVEC",
        "titulo": "Registrar unidad curricular",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_unidades",
        "mostrar_carga_masiva": True,
        "url_plantilla": "descargar_plantilla_unidad",
    })


@login_required
def modificar_unidad(request, unidad_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    unidad = get_object_or_404(
        UnidadCurricular,
        id=unidad_id,
        malla_curricular__carrera__campus__universidad=universidad_usuario
    )

    if request.method == "POST":
        formulario = FormularioUnidadCurricular(request.POST, instance=unidad)
        formulario.fields["malla_curricular"].queryset = MallaCurricular.objects.filter(
            carrera__campus__universidad=universidad_usuario
        )
        if formulario.is_valid():
            formulario.save()
            messages.success(
                request, "La unidad curricular ha sido modificada correctamente"
            )
            return redirect("listar_unidades")
    else:
        formulario = FormularioUnidadCurricular(instance=unidad)
        formulario.fields["malla_curricular"].queryset = MallaCurricular.objects.filter(
            carrera__campus__universidad=universidad_usuario
        )

    return render(request, "academico/formulario_unidad.html", {
        "formulario": formulario,
        "titulo_pagina": "Unidades curriculares - NIVEC",
        "titulo": "Modificar unidad curricular",
        "boton_texto": "Modificar",
        "url_cancelar": "listar_unidades",
        "mostrar_carga_masiva": False,
    })


@login_required
def eliminar_unidad(request, unidad_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    unidad = get_object_or_404(
        UnidadCurricular,
        id=unidad_id,
        malla_curricular__carrera__campus__universidad=universidad_usuario
    )
    unidad.delete()
    messages.success(request, "La unidad curricular ha sido eliminada correctamente")
    return redirect("listar_unidades")