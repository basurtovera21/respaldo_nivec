from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import ProtectedError
from django.http import HttpResponse
import openpyxl
from academico.models import Campus
from academico.forms import FormularioCampus
from academico.services import servicio_campus_registrar_masivo_desde_excel
from usuarios.utils import generar_identificador_siguiente, requiere_perfil, usuario_es_solo_lectura, ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR

@requiere_perfil(ROL_DIRECTOR_DAN, ROL_RECTOR, ROL_VICERRECTOR)
def listar_campus(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    campus = Campus.objects.filter(universidad=universidad_usuario).order_by("codigo_de_campus")

    busqueda = request.GET.get("busqueda", "").strip()
    if busqueda:
        campus = campus.filter(nombre__icontains=busqueda)

    tiene_registros = Campus.objects.filter(universidad=universidad_usuario).exists()
    
    return render(request, "entidades/listar_campus.html", {
        "campus": campus,
        "busqueda": busqueda,
        "tiene_registros": tiene_registros,
        "titulo_pagina": "Campus - NIVEC",
        "titulo": "Campus",
        "url_registrar": "registrar_campus",
        "texto_registrar": "Registrar",
        "url_volver": "panel_principal",
        "solo_lectura": usuario_es_solo_lectura(request.user),
    })
    
@requiere_perfil(ROL_DIRECTOR_DAN)
def descargar_plantilla_campus(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Campus"

    cabeceras = ["Nombre del Campus", "Dirección física", "Provincia"]
    ws.append(cabeceras)

    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 40
    ws.column_dimensions['C'].width = 40

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="campus_documento_nivec.xlsx"'
    wb.save(response)
    return response

@requiere_perfil(ROL_DIRECTOR_DAN)
def registrar_campus(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    if request.method == "POST":
        if 'archivo_excel' in request.FILES:
            archivo = request.FILES['archivo_excel']
            if not archivo.name.endswith('.xlsx'):
                messages.error(request, "Documento con formato no válido")
                return redirect("registrar_campus")
            
            resultado = servicio_campus_registrar_masivo_desde_excel(archivo, universidad_usuario)
            
            if resultado["error"]:
                messages.error(request, resultado["error"])
            
            for adv in resultado["advertencias"]:
                messages.warning(request, adv)
                
            if resultado["exitosos"] > 0:
                messages.success(request, f"{resultado['exitosos']} Campus han sido registrados correctamente")
            
            return redirect("listar_campus")

        else:
            formulario = FormularioCampus(request.POST, universidad=universidad_usuario)
            if 'codigo_de_campus' in formulario.fields:
                formulario.fields['codigo_de_campus'].required = False

            if formulario.is_valid():
                nuevo_campus = formulario.save(commit=False)
                nuevo_campus.universidad = universidad_usuario
                nuevo_campus.codigo_de_campus = generar_identificador_siguiente(Campus, 'CAM', 'codigo_de_campus')
                nuevo_campus.save()
                messages.success(request, "El Campus ha sido registrado correctamente")
                return redirect("listar_campus")
    else:
        formulario = FormularioCampus(universidad=universidad_usuario)
        
    return render(request, "entidades/formulario_campus.html", {
        "formulario": formulario,
        "titulo_pagina": "Campus - NIVEC",
        "titulo": "Registrar Campus",
        "boton_texto": "Registrar",
        "url_cancelar": "listar_campus",
        "mostrar_carga_masiva": True,
        "url_plantilla": "descargar_plantilla_campus"
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def modificar_campus(request, campus_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    campus = get_object_or_404(Campus, id=campus_id, universidad=universidad_usuario)

    if request.method == "POST":
        formulario = FormularioCampus(request.POST, instance=campus, universidad=universidad_usuario)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "El Campus ha sido modificado correctamente")
            return redirect("listar_campus")
    else:
        formulario = FormularioCampus(instance=campus, universidad=universidad_usuario)
        
    return render(request, "entidades/formulario_campus.html", {
        "formulario": formulario,
        "titulo_pagina": "Campus - NIVEC",
        "titulo": "Modificar Campus",
        "boton_texto": "Modificar",
        "url_cancelar": "listar_campus",
        "mostrar_carga_masiva": False
    })

@requiere_perfil(ROL_DIRECTOR_DAN)
def eliminar_campus(request, campus_id):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La Institución no ha sido registrada actualmente")
        return redirect("panel_principal")

    campus = get_object_or_404(Campus, id=campus_id, universidad=universidad_usuario)
    try:
        campus.delete()
        messages.success(request, "El Campus ha sido eliminado correctamente")
    except ProtectedError:
        messages.error(
            request,
            "No se ha podido eliminar el Campus (registros asociados)"
        )
    return redirect("listar_campus")