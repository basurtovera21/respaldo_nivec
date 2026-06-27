from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
import openpyxl

from academico.models import Carrera, Campus
from academico.forms import FormularioCarrera
from academico.services import servicio_carrera_registrar_masivo_desde_excel
from usuarios.utils import generar_identificador_siguiente, requiere_perfil, ROL_DIRECTOR_DAN

@requiere_perfil(ROL_DIRECTOR_DAN)
def listar_carreras(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    if not Campus.objects.filter(universidad=universidad_usuario).exists():
        messages.warning(request, "No existen registros de campus actualmente")
        return redirect("panel_principal")

    carreras = Carrera.objects.filter(campus__universidad=universidad_usuario).select_related("campus")
    
    return render(request, "entidades/listar_carreras.html", {
        "carreras": carreras,
        "titulo_pagina": "Carrera - NIVEC",
        "titulo": "Carreras",
        "url_registrar": "registrar_carrera",
        "texto_registrar": "Registrar",
        "url_volver": "panel_principal"
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def descargar_plantilla_carrera(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Carreras"

    cabeceras = [
        "Código de campus (CAM...)", 
        "Nombre de la carrera", 
        "Modalidad (Virtual, Presencial, Semipresencial)",
        "Facultad", 
        "Vigencia SNIESE (AAAA-MM-DD)"
    ]
    ws.append(cabeceras)

    for col in range(1, 6):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 40

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="formato_carreras_nivec.xlsx"'
    wb.save(response)
    return response

@requiere_perfil(ROL_DIRECTOR_DAN)
def registrar_carrera(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    campus_existente = Campus.objects.filter(universidad=universidad_usuario)
    if not campus_existente.exists():
        messages.warning(request, "No hay registros de campus actualmente")
        return redirect("panel_principal")

    if request.method == "POST":
        if 'archivo_excel' in request.FILES:
            resultado = servicio_carrera_registrar_masivo_desde_excel(request.FILES['archivo_excel'], universidad_usuario)
            
            if resultado["error"]: messages.error(request, resultado["error"])
            for adv in resultado["advertencias"]: messages.warning(request, adv)
            if resultado["exitosos"] > 0: messages.success(request, f"{resultado['exitosos']} carreras han sido registradas correctamente")
            return redirect("listar_carreras")

        else:
            formulario = FormularioCarrera(request.POST)
            if 'codigo_de_carrera' in formulario.fields:
                formulario.fields['codigo_de_carrera'].required = False

            if formulario.is_valid():
                nueva_carrera = formulario.save(commit=False)
                nueva_carrera.codigo_de_carrera = generar_identificador_siguiente(Carrera, 'CAR', 'codigo_de_carrera')
                nueva_carrera.save()
                messages.success(request, "La carrera ha sido registrada correctamente")
                return redirect("listar_carreras")
    else:
        formulario = FormularioCarrera()
        formulario.fields['campus'].queryset = campus_existente
        
    return render(request, "entidades/formulario_carrera.html", {
        "formulario": formulario,
        "titulo_pagina": "Carrera - NIVEC",
        "titulo": "Registrar carrera",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_carreras",
        "mostrar_carga_masiva": True,
        "url_plantilla": "descargar_plantilla_carrera"
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def modificar_carrera(request, carrera_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    carrera = get_object_or_404(Carrera, id=carrera_id, campus__universidad=universidad_usuario)

    if request.method == "POST":
        formulario = FormularioCarrera(request.POST, instance=carrera)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "La carrera ha sido modificada correctamente")
            return redirect("listar_carreras")
    else:
        formulario = FormularioCarrera(instance=carrera)
        formulario.fields['campus'].queryset = Campus.objects.filter(universidad=universidad_usuario)

    return render(request, "entidades/formulario_carrera.html", {
        "formulario": formulario,
        "titulo_pagina": "Carrera - NIVEC",
        "titulo": "Modificar carrera",
        "boton_texto": "Modificar",
        "url_cancelar": "listar_carreras",
        "mostrar_carga_masiva": False
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def eliminar_carrera(request, carrera_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente")
        return redirect("panel_principal")

    carrera = get_object_or_404(Carrera, id=carrera_id, campus__universidad=universidad_usuario)
    carrera.delete()
    messages.success(request, "La carrera ha sido eliminada correctamente")
    return redirect("listar_carreras")
