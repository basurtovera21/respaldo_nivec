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

    from academico.models import Campus, Carrera, PeriodoDeNivelacion, MallaCurricular, UnidadCurricular, Paralelo, Horario, ConsolidadoAcademico
    from academico.permisos import todas_calificaciones_formalizadas_por_carrera
    from poo.clases.enums.estado_de_periodo import EstadoDePeriodo as EP
    tiene_campus = Campus.objects.filter(universidad=perfil.universidad).exists() if perfil and perfil.universidad else False
    tiene_carreras = Carrera.objects.filter(campus__universidad=perfil.universidad).exists() if perfil and perfil.universidad else False
    tiene_periodos = PeriodoDeNivelacion.objects.filter(universidad=perfil.universidad).exists() if perfil and perfil.universidad else False
    tiene_mallas = MallaCurricular.objects.filter(carrera__campus__universidad=perfil.universidad).exists() if perfil and perfil.universidad else False
    tiene_unidades = UnidadCurricular.objects.filter(malla_curricular__carrera__campus__universidad=perfil.universidad).exists() if perfil and perfil.universidad else False
    tiene_paralelos = Paralelo.objects.filter(periodo_de_nivelacion__universidad=perfil.universidad).exists() if perfil and perfil.universidad else False
    tiene_horarios = Horario.objects.filter(paralelo__periodo_de_nivelacion__universidad=perfil.universidad).exists() if perfil and perfil.universidad else False
    tiene_consolidados = ConsolidadoAcademico.objects.filter(periodo_academico__universidad=perfil.universidad).exists() if perfil and perfil.universidad else False
    periodo_en_evaluacion_o_cerrado = PeriodoDeNivelacion.objects.filter(universidad=perfil.universidad, estado__in=[EP.EVALUACION.value, EP.CERRADO.value]).exists() if perfil and perfil.universidad else False
    puede_ver_informe = periodo_en_evaluacion_o_cerrado and todas_calificaciones_formalizadas_por_carrera(perfil.universidad) if perfil and perfil.universidad else False

    return render(request, "administrativo/panel_director_dan.html", {
        "tiene_universidad": tiene_universidad,
        "tiene_campus": tiene_campus,
        "tiene_carreras": tiene_carreras,
        "tiene_periodos": tiene_periodos,
        "tiene_mallas": tiene_mallas,
        "tiene_unidades": tiene_unidades,
        "tiene_paralelos": tiene_paralelos,
        "tiene_horarios": tiene_horarios,
        "tiene_consolidados": tiene_consolidados,
        "puede_ver_informe": puede_ver_informe,
    })

@login_required
@never_cache
def panel_dan(request):
    from academico.models import Campus, Carrera, PeriodoDeNivelacion, MallaCurricular, UnidadCurricular, Paralelo, Horario, ConsolidadoAcademico
    from academico.permisos import todas_calificaciones_formalizadas_por_carrera
    perfil = getattr(request.user, 'perfil_administrativo', None)
    universidad = perfil.universidad if perfil else None
    tiene_universidad = universidad is not None
    tiene_campus = Campus.objects.filter(universidad=universidad).exists() if universidad else False
    tiene_carreras = Carrera.objects.filter(campus__universidad=universidad).exists() if universidad else False
    tiene_periodos = PeriodoDeNivelacion.objects.filter(universidad=universidad).exists() if universidad else False
    tiene_mallas = MallaCurricular.objects.filter(carrera__campus__universidad=universidad).exists() if universidad else False
    tiene_unidades = UnidadCurricular.objects.filter(malla_curricular__carrera__campus__universidad=universidad).exists() if universidad else False
    tiene_paralelos = Paralelo.objects.filter(periodo_de_nivelacion__universidad=universidad).exists() if universidad else False
    tiene_horarios = Horario.objects.filter(paralelo__periodo_de_nivelacion__universidad=universidad).exists() if universidad else False
    tiene_consolidados = ConsolidadoAcademico.objects.filter(periodo_academico__universidad=universidad).exists() if universidad else False
    # Informe solo disponible cuando periodo está cerrado y al menos una carrera formalizada
    from poo.clases.enums.estado_de_periodo import EstadoDePeriodo as EP
    periodo_cerrado = PeriodoDeNivelacion.objects.filter(universidad=universidad, estado=EP.CERRADO.value).exists() if universidad else False
    puede_ver_informe = periodo_cerrado and todas_calificaciones_formalizadas_por_carrera(universidad) if universidad else False
    return render(request, "administrativo/panel_dan.html", {
        "tiene_universidad": tiene_universidad,
        "tiene_campus": tiene_campus,
        "tiene_carreras": tiene_carreras,
        "tiene_periodos": tiene_periodos,
        "tiene_mallas": tiene_mallas,
        "tiene_unidades": tiene_unidades,
        "tiene_paralelos": tiene_paralelos,
        "tiene_horarios": tiene_horarios,
        "tiene_consolidados": tiene_consolidados,
        "puede_ver_informe": puede_ver_informe,
    })
    return render(request, "administrativo/panel_dan.html", {
        "tiene_universidad": tiene_universidad,
        "tiene_campus": tiene_campus,
        "tiene_carreras": tiene_carreras,
        "tiene_periodos": tiene_periodos,
        "tiene_mallas": tiene_mallas,
    })

@login_required
@never_cache
def panel_ua(request):
    usuario = request.user
    perfil = getattr(usuario, 'perfil_administrativo', None)
    if not perfil:
        return redirect('panel_principal')
    
    carrera = perfil.carrera_asignada
    universidad = perfil.universidad

    from academico.models import PeriodoDeNivelacion, Carrera as CarreraModel, MallaCurricular, Paralelo, Horario
    from usuarios.models import PerfilEstudiante
    from academico.permisos import todas_calificaciones_formalizadas_por_carrera
    from poo.clases.enums.estado_de_periodo import EstadoDePeriodo as EP

    tiene_periodos = PeriodoDeNivelacion.objects.filter(universidad=universidad).exists() if universidad else False
    tiene_carreras = CarreraModel.objects.filter(campus__universidad=universidad).exists() if universidad else False
    tiene_estudiantes = PerfilEstudiante.objects.filter(carrera_registrada=carrera).exists() if carrera else False
    tiene_mallas = MallaCurricular.objects.filter(carrera__campus__universidad=universidad).exists() if universidad else False
    tiene_paralelos = Paralelo.objects.filter(
        periodo_de_nivelacion__universidad=universidad,
        unidad_curricular__malla_curricular__carrera=carrera,
    ).exists() if (universidad and carrera) else False
    tiene_horarios = Horario.objects.filter(
        paralelo__periodo_de_nivelacion__universidad=universidad,
        paralelo__unidad_curricular__malla_curricular__carrera=carrera,
    ).exists() if (universidad and carrera) else False
    periodo_en_evaluacion_o_cerrado = PeriodoDeNivelacion.objects.filter(universidad=universidad, estado__in=[EP.EVALUACION.value, EP.CERRADO.value]).exists() if universidad else False
    puede_ver_informe = periodo_en_evaluacion_o_cerrado and todas_calificaciones_formalizadas_por_carrera(universidad, carrera) if universidad else False

    return render(request, "administrativo/panel_ua.html", {
        "perfil": perfil,
        "carrera": carrera,
        "tiene_periodos": tiene_periodos,
        "tiene_carreras": tiene_carreras,
        "tiene_estudiantes": tiene_estudiantes,
        "tiene_mallas": tiene_mallas,
        "tiene_paralelos": tiene_paralelos,
        "tiene_horarios": tiene_horarios,
        "puede_ver_informe": puede_ver_informe,
    })

@login_required
@never_cache
def panel_administrativo(request):
    from academico.models import Campus, Carrera, PeriodoDeNivelacion, MallaCurricular, UnidadCurricular, ConsolidadoAcademico, Paralelo, Horario
    from usuarios.models import PerfilAdministrativo as PAModel, PerfilDocente, PerfilEstudiante
    from poo.clases.enums.perfil_administrativo import PerfilAdministrativo as EnumPA
    perfil = getattr(request.user, 'perfil_administrativo', None)
    universidad = perfil.universidad if perfil else None
    tiene_universidad = universidad is not None
    tiene_campus = Campus.objects.filter(universidad=universidad).exists() if universidad else False
    tiene_carreras = Carrera.objects.filter(campus__universidad=universidad).exists() if universidad else False
    tiene_periodos = PeriodoDeNivelacion.objects.filter(universidad=universidad).exists() if universidad else False
    tiene_mallas = MallaCurricular.objects.filter(carrera__campus__universidad=universidad).exists() if universidad else False
    tiene_unidades = UnidadCurricular.objects.filter(malla_curricular__carrera__campus__universidad=universidad).exists() if universidad else False
    tiene_administrativos = PAModel.objects.filter(universidad=universidad).exclude(perfil_administrativo__in=[EnumPA.COORDINADOR_DAN.value, EnumPA.COORDINADOR_UA.value]).exists() if universidad else False
    tiene_coordinadores_dan = PAModel.objects.filter(universidad=universidad, perfil_administrativo=EnumPA.COORDINADOR_DAN.value).exists() if universidad else False
    tiene_coordinadores_ua = PAModel.objects.filter(universidad=universidad, perfil_administrativo=EnumPA.COORDINADOR_UA.value).exists() if universidad else False
    tiene_docentes = PerfilDocente.objects.filter(universidad=universidad).exists() if universidad else False
    tiene_estudiantes = PerfilEstudiante.objects.filter(carrera_registrada__campus__universidad=universidad).exists() if universidad else False
    tiene_algun_usuario = tiene_administrativos or tiene_coordinadores_dan or tiene_coordinadores_ua or tiene_docentes or tiene_estudiantes
    tiene_algun_institucional = tiene_campus or tiene_carreras or tiene_periodos
    tiene_consolidados = ConsolidadoAcademico.objects.filter(periodo_academico__universidad=universidad).exists() if universidad else False
    tiene_paralelos = Paralelo.objects.filter(periodo_de_nivelacion__universidad=universidad).exists() if universidad else False
    tiene_horarios = Horario.objects.filter(paralelo__periodo_de_nivelacion__universidad=universidad).exists() if universidad else False
    return render(request, "administrativo/panel_administrativo.html", {
        "tiene_universidad": tiene_universidad,
        "tiene_campus": tiene_campus,
        "tiene_carreras": tiene_carreras,
        "tiene_periodos": tiene_periodos,
        "tiene_mallas": tiene_mallas,
        "tiene_unidades": tiene_unidades,
        "tiene_administrativos": tiene_administrativos,
        "tiene_coordinadores_dan": tiene_coordinadores_dan,
        "tiene_coordinadores_ua": tiene_coordinadores_ua,
        "tiene_docentes": tiene_docentes,
        "tiene_estudiantes": tiene_estudiantes,
        "tiene_algun_usuario": tiene_algun_usuario,
        "tiene_algun_institucional": tiene_algun_institucional,
        "tiene_consolidados": tiene_consolidados,
        "tiene_paralelos": tiene_paralelos,
        "tiene_horarios": tiene_horarios,
    })

@login_required
@never_cache
def panel_docente(request):
    usuario = request.user
    perfil_docente = getattr(usuario, 'perfil_docente', None)
    if not perfil_docente:
        return redirect('panel_principal')
    
    from academico.models import Paralelo, PeriodoDeNivelacion, Horario
    from academico.permisos import obtener_permisos_periodo
    from poo.clases.enums.estado_de_periodo import EstadoDePeriodo
    from poo.clases.enums.dia_de_semana import DiaDeSemana
    from poo.clases.enums.jornada import Jornada
    from poo.clases.franja_horaria import obtener_franja
    
    universidad = perfil_docente.universidad
    
    # Obtener periodo activo (no cerrado) - prioridad: En Curso > Evaluación > Planificación
    periodo_actual = None
    if universidad:
        for estado_buscar in [EstadoDePeriodo.EN_CURSO.value, EstadoDePeriodo.EVALUACION.value, EstadoDePeriodo.PLANIFICACION.value]:
            p = PeriodoDeNivelacion.objects.filter(universidad=universidad, estado=estado_buscar).first()
            if p:
                periodo_actual = p
                break
    
    # Obtener paralelos donde este docente es responsable en el periodo activo
    paralelos = []
    tiene_horarios = False
    horarios_list = []
    grilla = []
    dias_semana = [d.value for d in DiaDeSemana]
    mapa_colores = {}

    if periodo_actual:
        paralelos = list(Paralelo.objects.filter(
            periodo_de_nivelacion=periodo_actual,
            docente_responsable=perfil_docente,
        ).select_related("unidad_curricular__malla_curricular__carrera").order_by("nombre", "unidad_curricular__nombre"))

        # Construir grilla de horarios desde los paralelos asignados
        if paralelos:
            paralelo_ids = [p.id for p in paralelos]
            from django.db.models import Case, When, Value, IntegerField
            dias_orden = {
                "Lunes": 1, "Martes": 2, "Miércoles": 3, "Miercoles": 3,
                "Jueves": 4, "Viernes": 5, "Sábado": 6, "Sabado": 6, "Domingo": 7,
            }
            horarios = Horario.objects.filter(
                paralelo_id__in=paralelo_ids
            ).select_related("paralelo__unidad_curricular").annotate(
                dia_orden=Case(
                    *[When(dia_semana=dia, then=Value(orden)) for dia, orden in dias_orden.items()],
                    default=Value(8),
                    output_field=IntegerField(),
                )
            ).order_by("dia_orden", "hora_inicio")
            
            tiene_horarios = horarios.exists()
            horarios_list = list(horarios)

            if tiene_horarios:
                # Determinar franja desde la jornada del primer paralelo
                try:
                    jornada_enum = Jornada(paralelos[0].jornada)
                    franja = obtener_franja(jornada_enum)
                except (ValueError, KeyError):
                    franja = None

                if franja:
                    slots_hora = list(range(franja[0].hour, franja[1].hour))
                    _COLORES_UNIDAD = [
                        "#e8e8ed", "#d2e4ea", "#dce8d4", "#f0e6d2", "#e2d8ef",
                        "#d8eef0", "#f5e0d8", "#d4e8e0", "#ede4d0", "#dfe0f5",
                    ]
                    nombres_unidades = sorted(set(h.paralelo.unidad_curricular.nombre for h in horarios))
                    mapa_colores = {nombre: _COLORES_UNIDAD[i % len(_COLORES_UNIDAD)] for i, nombre in enumerate(nombres_unidades)}

                    for slot in slots_hora:
                        fila = {"hora": f"{slot:02d}:00", "celdas": []}
                        for dia in dias_semana:
                            bloque = None
                            for h in horarios:
                                if h.dia_semana == dia and h.hora_inicio.hour <= slot < h.hora_fin.hour:
                                    bloque = {
                                        "nombre": h.paralelo.unidad_curricular.nombre,
                                        "slot_inicio": f"{slot:02d}:00",
                                        "slot_fin": f"{slot+1:02d}:00",
                                        "color": mapa_colores.get(h.paralelo.unidad_curricular.nombre, "#e8e8ed"),
                                    }
                                    break
                            fila["celdas"].append(bloque)
                        grilla.append(fila)

    # Aviso de estado
    permisos = obtener_permisos_periodo(universidad) if universidad else {}
    estado = permisos.get("estado_periodo", "")
    aviso_estado = ""
    if estado == "PLANIFICACION":
        aviso_estado = "El Periodo de nivelación se encuentra en planificación"
    elif estado == "EN_CURSO":
        aviso_estado = "El Periodo de nivelación se encuentra en curso"
    elif estado == "EVALUACION":
        aviso_estado = "El Periodo de nivelación se encuentra en evaluación"
    elif estado in ("SOLO_CERRADOS", "CERRADO"):
        aviso_estado = "El Periodo de nivelación ha finalizado"

    return render(request, "docente/panel_docente.html", {
        "perfil_docente": perfil_docente,
        "periodo_actual": periodo_actual,
        "paralelos": paralelos,
        "tiene_horarios": tiene_horarios,
        "horarios": horarios_list,
        "grilla": grilla,
        "dias_semana": dias_semana,
        "mapa_colores": mapa_colores,
        "aviso_estado": aviso_estado,
        "puede_ver_calificaciones": permisos.get("puede_ver_calificaciones", False),
    })

@login_required
@never_cache
def panel_estudiante(request):
    usuario = request.user
    perfil_estudiante = PerfilEstudiante.objects.filter(usuario_de_sistema=usuario).first()
    if not perfil_estudiante:
        return redirect('cerrar_sesion')
    
    from academico.models import Paralelo, MatriculaParalelo, Horario, EvaluacionAcademica, PeriodoDeNivelacion
    from academico.permisos import obtener_permisos_periodo
    
    periodo = perfil_estudiante.periodo_de_nivelacion
    universidad = perfil_estudiante.carrera_registrada.campus.universidad if perfil_estudiante.carrera_registrada else None
    
    # Obtener paralelo(s) donde el estudiante está matriculado
    matriculas = MatriculaParalelo.objects.filter(
        estudiante=perfil_estudiante,
        paralelo__periodo_de_nivelacion=periodo,
    ).select_related(
        "paralelo__unidad_curricular__malla_curricular__carrera",
        "paralelo__docente_responsable__usuario_de_sistema",
    ).order_by("paralelo__nombre", "paralelo__unidad_curricular__nombre") if periodo else MatriculaParalelo.objects.none()

    # Obtener evaluaciones
    evaluaciones = EvaluacionAcademica.objects.filter(
        estudiante=perfil_estudiante,
        periodo_de_nivelacion=periodo,
    ).select_related("unidad_curricular").order_by("unidad_curricular__nombre") if periodo else EvaluacionAcademica.objects.none()

    # Obtener horarios
    paralelo_ids = [m.paralelo_id for m in matriculas]
    if paralelo_ids:
        from django.db.models import Case, When, Value, IntegerField
        dias_orden_est = {
            "Lunes": 1, "Martes": 2, "Miércoles": 3, "Miercoles": 3,
            "Jueves": 4, "Viernes": 5, "Sábado": 6, "Sabado": 6, "Domingo": 7,
        }
        horarios = Horario.objects.filter(
            paralelo_id__in=paralelo_ids
        ).select_related("paralelo__unidad_curricular").annotate(
            dia_orden=Case(
                *[When(dia_semana=dia, then=Value(orden)) for dia, orden in dias_orden_est.items()],
                default=Value(8),
                output_field=IntegerField(),
            )
        ).order_by("dia_orden", "hora_inicio")
    else:
        horarios = Horario.objects.none()

    # Construir grilla visual del horario del estudiante
    from poo.clases.enums.dia_de_semana import DiaDeSemana
    from poo.clases.enums.jornada import Jornada
    from poo.clases.franja_horaria import obtener_franja

    grilla = []
    dias_semana = [d.value for d in DiaDeSemana]
    mapa_colores = {}

    if horarios.exists():
        # Determinar franja desde la jornada del estudiante
        jornada_estudiante = perfil_estudiante.jornada
        try:
            jornada_enum = Jornada(jornada_estudiante)
            franja = obtener_franja(jornada_enum)
        except (ValueError, KeyError):
            franja = None

        if franja:
            slots_hora = list(range(franja[0].hour, franja[1].hour))

            _COLORES_UNIDAD = [
                "#e8e8ed", "#d2e4ea", "#dce8d4", "#f0e6d2", "#e2d8ef",
                "#d8eef0", "#f5e0d8", "#d4e8e0", "#ede4d0", "#dfe0f5",
            ]
            nombres_unidades = sorted(set(h.paralelo.unidad_curricular.nombre for h in horarios))
            mapa_colores = {nombre: _COLORES_UNIDAD[i % len(_COLORES_UNIDAD)] for i, nombre in enumerate(nombres_unidades)}

            for slot in slots_hora:
                fila = {"hora": f"{slot:02d}:00", "celdas": []}
                for dia in dias_semana:
                    bloque = None
                    for h in horarios:
                        if h.dia_semana == dia and h.hora_inicio.hour <= slot < h.hora_fin.hour:
                            bloque = {
                                "nombre": h.paralelo.unidad_curricular.nombre,
                                "slot_inicio": f"{slot:02d}:00",
                                "slot_fin": f"{slot+1:02d}:00",
                                "color": mapa_colores.get(h.paralelo.unidad_curricular.nombre, "#e8e8ed"),
                            }
                            break
                    fila["celdas"].append(bloque)
                grilla.append(fila)

    # Aviso de estado y permisos
    permisos = obtener_permisos_periodo(universidad) if universidad else {}
    estado = permisos.get("estado_periodo", "")
    aviso_estado = ""
    if estado == "PLANIFICACION":
        aviso_estado = "El Periodo de nivelación se encuentra en planificación"
    elif estado == "EN_CURSO":
        aviso_estado = "El Periodo de nivelación se encuentra en curso"
    elif estado == "EVALUACION":
        aviso_estado = "El Periodo de nivelación se encuentra en evaluación"
    elif estado in ("SOLO_CERRADOS", "CERRADO"):
        aviso_estado = "El Periodo de nivelación ha finalizado"

    return render(request, "estudiante/panel_estudiante.html", {
        "perfil_estudiante": perfil_estudiante,
        "periodo": periodo,
        "matriculas": matriculas,
        "evaluaciones": evaluaciones,
        "horarios": horarios,
        "grilla": grilla,
        "dias_semana": dias_semana,
        "mapa_colores": mapa_colores,
        "aviso_estado": aviso_estado,
        "puede_ver_calificaciones": permisos.get("puede_ver_calificaciones", False),
    })