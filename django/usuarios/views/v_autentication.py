from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from usuarios import services
from usuarios.models import PerfilAdministrativo, PerfilDocente, PerfilEstudiante
from poo.clases.enums.perfil_administrativo import PerfilAdministrativo as EnumPerfilAdministrativo

@never_cache
def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("panel_principal")
    if request.method == "POST":
        correo_institucional = request.POST.get("correo_institucional")
        contrasena = request.POST.get("contrasena")
        resultado_inicio = services.servicio_iniciar_sesion(request, correo_institucional, contrasena)
        if resultado_inicio["exito"]:
            return redirect("panel_principal")
        messages.error(request, resultado_inicio["mensaje"])
    return render(request, "autenticacion/iniciar_sesion.html")


@login_required
def cerrar_sesion(request):
    services.servicio_cerrar_sesion(request)
    return redirect("iniciar_sesion")




@login_required
@never_cache
def panel_principal(request):
    usuario = request.user
    perfil_administrativo = PerfilAdministrativo.objects.filter(usuario_de_sistema=usuario).first()
    if perfil_administrativo:
        tipo_de_perfil = perfil_administrativo.perfil_administrativo
        if tipo_de_perfil == EnumPerfilAdministrativo.COORDINADOR_UA.value:
            return redirect('panel_ua')
        elif tipo_de_perfil == EnumPerfilAdministrativo.DIRECTOR_DAN.value:
            return redirect('panel_director_dan')  
        elif tipo_de_perfil == EnumPerfilAdministrativo.COORDINADOR_DAN.value:
            return redirect('panel_dan')  
        else:
            return redirect('panel_administrativo')
               
    elif PerfilDocente.objects.filter(usuario_de_sistema=usuario).exists():
        return redirect('panel_docente')
     
    elif PerfilEstudiante.objects.filter(usuario_de_sistema=usuario).exists():
        return redirect('panel_estudiante') 
    return redirect('cerrar_sesion')


@login_required
@never_cache
def panel_director_dan(request):
    tiene_universidad = False
    perfil = getattr(request.user, 'perfil_administrativo', None)
    if perfil and perfil.universidad:
        tiene_universidad = True
    return render(request, "administrativo/panel_director_dan.html", {
        "tiene_universidad": tiene_universidad,
    })

@login_required
@never_cache
def panel_dan(request):
    return render(request, "administrativo/panel_dan.html")

@login_required
@never_cache
def panel_ua(request):
    usuario = request.user
    perfil = getattr(usuario, 'perfil_administrativo', None)
    if not perfil:
        return redirect('panel_principal')
    
    carrera = perfil.carrera_asignada
    universidad = perfil.universidad


    from academico.models import Paralelo, PeriodoDeNivelacion
    
    periodos = PeriodoDeNivelacion.objects.filter(universidad=universidad).order_by('-anio', '-numero_periodo')
    
    paralelos = []
    periodo_actual = None
    if carrera:
        periodo_actual = periodos.first()
        if periodo_actual:
            paralelos = Paralelo.objects.filter(
                periodo_de_nivelacion=periodo_actual,
                unidad_curricular__malla_curricular__carrera=carrera,
            ).select_related("unidad_curricular").order_by("nombre", "unidad_curricular__nombre")
    
    # Count evaluaciones pending formalization for this carrera
    from academico.models import EvaluacionAcademica
    pendientes_formalizar = 0
    if carrera and periodo_actual:
        pendientes_formalizar = EvaluacionAcademica.objects.filter(
            periodo_de_nivelacion=periodo_actual,
            estudiante__carrera_registrada=carrera,
            estado_revision="En revisión",
        ).count()

    return render(request, "administrativo/panel_ua.html", {
        "perfil": perfil,
        "carrera": carrera,
        "periodo_actual": periodo_actual,
        "paralelos": paralelos,
        "pendientes_formalizar": pendientes_formalizar,
    })

@login_required
@never_cache
def panel_administrativo(request):
    return render(request, "administrativo/panel_administrativo.html")

@login_required
@never_cache
def panel_docente(request):
    usuario = request.user
    perfil_docente = getattr(usuario, 'perfil_docente', None)
    if not perfil_docente:
        return redirect('panel_principal')
    
    from academico.models import Paralelo, PeriodoDeNivelacion
    
    universidad = perfil_docente.universidad
    periodos = PeriodoDeNivelacion.objects.filter(universidad=universidad).order_by('-anio', '-numero_periodo') if universidad else PeriodoDeNivelacion.objects.none()
    periodo_actual = periodos.first()
    
    # Get paralelos where this docente is responsible
    paralelos = []
    if periodo_actual:
        paralelos = Paralelo.objects.filter(
            periodo_de_nivelacion=periodo_actual,
            docente_responsable=perfil_docente,
        ).select_related("unidad_curricular__malla_curricular__carrera").order_by("nombre", "unidad_curricular__nombre")
    
    return render(request, "docente/panel_docente.html", {
        "perfil_docente": perfil_docente,
        "periodo_actual": periodo_actual,
        "paralelos": paralelos,
    })

@login_required
@never_cache
def panel_estudiante(request):
    usuario = request.user
    perfil_estudiante = PerfilEstudiante.objects.filter(usuario_de_sistema=usuario).first()
    if not perfil_estudiante:
        return redirect('cerrar_sesion')
    
    from academico.models import Paralelo, MatriculaParalelo, Horario, EvaluacionAcademica, PeriodoDeNivelacion
    
    periodo = perfil_estudiante.periodo_de_nivelacion
    
    # Get paralelo(s) where the student is enrolled
    matriculas = MatriculaParalelo.objects.filter(
        estudiante=perfil_estudiante,
        paralelo__periodo_de_nivelacion=periodo,
    ).select_related(
        "paralelo__unidad_curricular__malla_curricular__carrera",
        "paralelo__docente_responsable__usuario_de_sistema",
    ).order_by("paralelo__nombre", "paralelo__unidad_curricular__nombre") if periodo else MatriculaParalelo.objects.none()

    # Get evaluaciones
    evaluaciones = EvaluacionAcademica.objects.filter(
        estudiante=perfil_estudiante,
        periodo_de_nivelacion=periodo,
    ).select_related("unidad_curricular").order_by("unidad_curricular__nombre") if periodo else EvaluacionAcademica.objects.none()

    # Get horarios
    paralelo_ids = [m.paralelo_id for m in matriculas]
    horarios = Horario.objects.filter(
        paralelo_id__in=paralelo_ids
    ).select_related("paralelo__unidad_curricular").order_by("dia_semana", "hora_inicio") if paralelo_ids else Horario.objects.none()

    return render(request, "estudiante/panel_estudiante.html", {
        "perfil_estudiante": perfil_estudiante,
        "periodo": periodo,
        "matriculas": matriculas,
        "evaluaciones": evaluaciones,
        "horarios": horarios,
    })