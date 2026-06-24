from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import openpyxl

from academico.models import Paralelo, PeriodoDeNivelacion, UnidadCurricular
from academico.forms import FormularioParalelo
from academico.services import servicio_paralelo_registrar_masivo_desde_excel
from usuarios.utils import generar_identificador_siguiente


@login_required
def listar_paralelos(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    periodo_id = request.GET.get("periodo")
    periodos = PeriodoDeNivelacion.objects.filter(universidad=universidad_usuario)

    paralelos = Paralelo.objects.filter(
        periodo_de_nivelacion__universidad=universidad_usuario
    ).select_related(
        "periodo_de_nivelacion",
        "unidad_curricular",
        "docente_responsable__usuario_de_sistema"
    )

    if periodo_id:
        paralelos = paralelos.filter(periodo_de_nivelacion__id=periodo_id)

    periodo_seleccionado = None
    if periodo_id:
        periodo_seleccionado = periodos.filter(id=periodo_id).first()

    return render(request, "academico/listar_paralelos.html", {
        "paralelos": paralelos,
        "periodos": periodos,
        "periodo_seleccionado": periodo_seleccionado,
        "titulo_pagina": "Paralelos - NIVEC",
        "titulo": "Paralelos",
        "url_registrar": "registrar_paralelo",
        "texto_registrar": "Registrar",
        "url_volver": "panel_dan"
    })


@login_required
def descargar_plantilla_paralelo(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Paralelos"

    cabeceras = [
        "Código de periodo (PNV...)",
        "Código de unidad curricular (UC...)",
        "Nombre del paralelo",
        "Jornada (Matutina, Vespertina, Nocturna)",
        "Modalidad (Virtual, Presencial, Semipresencial)",
        "Capacidad máxima (número entero)",
    ]
    ws.append(cabeceras)

    for col in range(1, len(cabeceras) + 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 40

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="formato_paralelos_nivec.xlsx"'
    wb.save(response)
    return response


@login_required
def registrar_paralelo(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    periodos_existentes = PeriodoDeNivelacion.objects.filter(universidad=universidad_usuario)
    unidades_existentes = UnidadCurricular.objects.filter(
        malla_curricular__carrera__campus__universidad=universidad_usuario
    )

    if not periodos_existentes.exists():
        messages.warning(request, "No existen registros de periodos de nivelación actualmente")
        return redirect("panel_dan")

    if not unidades_existentes.exists():
        messages.warning(request, "No existen registros de unidades curriculares actualmente")
        return redirect("panel_dan")

    if request.method == "POST":
        if "archivo_excel" in request.FILES:
            archivo = request.FILES["archivo_excel"]
            if not archivo.name.endswith(".xlsx"):
                messages.error(request, "Documento con formato no válido")
                return redirect("registrar_paralelo")

            resultado = servicio_paralelo_registrar_masivo_desde_excel(archivo, universidad_usuario)

            if resultado["error"]:
                messages.error(request, resultado["error"])
            for adv in resultado["advertencias"]:
                messages.warning(request, adv)
            if resultado["exitosos"] > 0:
                messages.success(
                    request,
                    f"{resultado['exitosos']} paralelos registrados correctamente"
                )
            return redirect("listar_paralelos")

        else:
            formulario = FormularioParalelo(request.POST)
            formulario.fields["periodo_de_nivelacion"].queryset = periodos_existentes
            formulario.fields["unidad_curricular"].queryset = unidades_existentes

            if formulario.is_valid():
                nuevo_paralelo = formulario.save(commit=False)
                nuevo_paralelo.codigo_de_paralelo = generar_identificador_siguiente(
                    Paralelo, "PAR", "codigo_de_paralelo"
                )
                nuevo_paralelo.save()
                messages.success(request, "El paralelo ha sido registrado correctamente")
                return redirect("listar_paralelos")
    else:
        formulario = FormularioParalelo()
        formulario.fields["periodo_de_nivelacion"].queryset = periodos_existentes
        formulario.fields["unidad_curricular"].queryset = unidades_existentes

    return render(request, "academico/formulario_paralelo.html", {
        "formulario": formulario,
        "titulo_pagina": "Paralelos - NIVEC",
        "titulo": "Registrar paralelo",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_paralelos",
        "mostrar_carga_masiva": True,
        "url_plantilla": "descargar_plantilla_paralelo",
    })


@login_required
def modificar_paralelo(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo,
        id=paralelo_id,
        periodo_de_nivelacion__universidad=universidad_usuario
    )

    if request.method == "POST":
        formulario = FormularioParalelo(request.POST, instance=paralelo)
        formulario.fields["periodo_de_nivelacion"].queryset = PeriodoDeNivelacion.objects.filter(
            universidad=universidad_usuario
        )
        formulario.fields["unidad_curricular"].queryset = UnidadCurricular.objects.filter(
            malla_curricular__carrera__campus__universidad=universidad_usuario
        )
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "El paralelo ha sido modificado correctamente")
            return redirect("listar_paralelos")
    else:
        formulario = FormularioParalelo(instance=paralelo)
        formulario.fields["periodo_de_nivelacion"].queryset = PeriodoDeNivelacion.objects.filter(
            universidad=universidad_usuario
        )
        formulario.fields["unidad_curricular"].queryset = UnidadCurricular.objects.filter(
            malla_curricular__carrera__campus__universidad=universidad_usuario
        )

    return render(request, "academico/formulario_paralelo.html", {
        "formulario": formulario,
        "titulo_pagina": "Paralelos - NIVEC",
        "titulo": "Modificar paralelo",
        "boton_texto": "Modificar",
        "url_cancelar": "listar_paralelos",
        "mostrar_carga_masiva": False,
    })


@login_required
def eliminar_paralelo(request, paralelo_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    paralelo = get_object_or_404(
        Paralelo,
        id=paralelo_id,
        periodo_de_nivelacion__universidad=universidad_usuario
    )
    paralelo.delete()
    messages.success(request, "El paralelo ha sido eliminado correctamente")
    return redirect("listar_paralelos")