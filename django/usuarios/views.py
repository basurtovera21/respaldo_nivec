from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.views.decorators.cache import never_cache

from .models import UsuarioDeSistema
from .models import PerfilDocente
from .models import PerfilEstudiante
from .models import PerfilAdministrativo

from .forms import FormularioUsuarioDeSistema
from .forms import FormularioPerfilEstudiante
from .forms import FormularioPerfilDocente
from .forms import FormularioPerfilAdministrativo

from . import services


#Autenticación
@never_cache
def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("panel_principal")
    
    if request.method == "POST":
        correo_institucional = request.POST.get("correo_institucional")
        contrasena = request.POST.get("contrasena")
        inicio_sesion = services.servicio_iniciar_sesion(request, correo_institucional, contrasena)
        
        if inicio_sesion:
            return redirect("panel_principal")
        
        messages.error(request, "Las credenciales registradas no son válidas.")
    
    return render(request, "autenticacion/iniciar_sesion.html")


@login_required
def cerrar_sesion(request):
    services.servicio_cerrar_sesion(request)
    return redirect("iniciar_sesion")


def panel_sin_perfil(request):
    return render(request, "autenticacion/sin_perfil.html")


@login_required
@never_cache
def panel_principal(request):
    usuario = request.user
    
    perfil_administrativo = PerfilAdministrativo.objects.filter(usuario_de_sistema=usuario).first()
    
    if perfil_administrativo:
        tipo_de_perfil = perfil_administrativo.perfil_administrativo

        if tipo_de_perfil == 'COORDINADOR_UA':
            return redirect('panel_ua')
        
        elif tipo_de_perfil == 'DIRECTOR_DAN':
            return redirect('panel_director_dan')
            
        elif tipo_de_perfil == 'COORDINADOR_DAN':
            return redirect('panel_dan')
            
        else:
            return redirect('panel_administrativo')
            
            
    elif PerfilDocente.objects.filter(usuario_de_sistema=usuario).exists():
        return redirect('panel_docente')
        
    elif PerfilEstudiante.objects.filter(usuario_de_sistema=usuario).exists():
        return redirect('panel_estudiante')
        
    return redirect('sin_perfil')


@login_required
@never_cache
def panel_director_dan(request):
    return render(request, "administrativo/panel_director_dan.html")


#Panel por tipo de usuario de sistema
@login_required
def panel_dan(request):
    from academico.models import PeriodoDeNivelacion, ConsolidadoAcademico
    periodos_de_nivelacion = PeriodoDeNivelacion.objects.all().order_by("-anio")
    consolidados_academicos = ConsolidadoAcademico.objects.all()
    return render(request, "dan/panel_dan.html", {
        "periodos_de_nivelacion": periodos_de_nivelacion,
        "consolidados_academicos": consolidados_academicos,
    })


@login_required
def panel_coordinador_ua(request):
    from academico.models import Paralelo
    paralelos = Paralelo.objects.all().order_by("periodo_de_nivelacion")
    docentes = PerfilDocente.objects.filter(estado_de_vinculacion="Activo")
    return render(request, "coordinador_ua/panel_coordinador_ua.html", {
        "paralelos": paralelos,
        "docentes": docentes,
    })


@login_required
def panel_docente(request):
    try:
        perfil_docente = request.user.perfil_docente
        from academico.models import Paralelo
        paralelos = Paralelo.objects.filter(docente_responsable=perfil_docente)
        carga_academica = services.servicio_obtener_carga_academica(perfil_docente)
        return render(request, "docente/panel_docente.html", {
            "perfil_docente": perfil_docente,
            "paralelos": paralelos,
            "carga": carga_academica,
        })
    except PerfilDocente.DoesNotExist:
        return redirect("panel_principal")


@login_required
def panel_estudiante(request):
    try:
        perfil_estudiante = request.user.perfil_estudiante
        from academico.models import MatriculaParalelo, EvaluacionAcademica
        matriculas = MatriculaParalelo.objects.filter(
            estudiante=perfil_estudiante
        ).select_related("paralelo", "paralelo__unidad_curricular")
        evaluaciones = EvaluacionAcademica.objects.filter(estudiante=perfil_estudiante)
        registro = services.servicio_obtener_registro_institucional(perfil_estudiante)
        return render(request, "estudiante/panel_estudiante.html", {
            "perfil_estudiante": perfil_estudiante,
            "matriculas": matriculas,
            "evaluaciones": evaluaciones,
            "registro": registro,
        })
    except PerfilEstudiante.DoesNotExist:
        return redirect("panel_principal")

@login_required
def panel_administrativo(request):
    # Esto apunta a la carpeta 'administrativo' y al archivo 'panel_director_dan.html'
    return render(request, "administrativo/panel_director_dan.html", {
        "titulo": "Panel Administrativo",
    })


#Usuarios
@login_required
def listar_usuarios(request):
    usuarios = UsuarioDeSistema.objects.all()
    return render(request, "usuarios/listar_usuarios.html", {"usuarios": usuarios})


@login_required
def registrar_usuario(request):
    if request.method == "POST":
        formulario = FormularioUsuarioDeSistema(request.POST)
        if formulario.is_valid():
            usuario = formulario.save(commit=False)
            usuario.set_password(formulario.cleaned_data["contrasena"])
            usuario.save()
            messages.success(request, "Usuario registrado correctamente.")
            return redirect("listar_usuarios")
    else:
        formulario = FormularioUsuarioDeSistema()
    return render(request, "usuarios/formulario_usuario.html", {
        "formulario": formulario,
        "titulo": "Registrar usuario",
    })


@login_required
def listar_docentes(request):
    docentes = PerfilDocente.objects.all().select_related("usuario_de_sistema")
    return render(request, "usuarios/listar_docentes.html", {"docentes": docentes})


@login_required
def registrar_docente(request):
    if request.method == "POST":
        formulario_usuario = FormularioUsuarioDeSistema(request.POST)
        formulario_perfil = FormularioPerfilDocente(request.POST)
        if formulario_usuario.is_valid() and formulario_perfil.is_valid():
            usuario = formulario_usuario.save(commit=False)
            usuario.set_password(formulario_usuario.cleaned_data["contrasena"])
            usuario.save()
            perfil = formulario_perfil.save(commit=False)
            perfil.usuario_de_sistema = usuario
            perfil.save()
            messages.success(request, "Docente registrado correctamente.")
            return redirect("listar_docentes")
    else:
        formulario_usuario = FormularioUsuarioDeSistema()
        formulario_perfil = FormularioPerfilDocente()
    return render(request, "usuarios/formulario_docente.html", {
        "formulario_usuario": formulario_usuario,
        "formulario_perfil": formulario_perfil,
        "titulo": "Registrar docente",
    })


@login_required
def listar_estudiantes(request):
    estudiantes = PerfilEstudiante.objects.all().select_related(
        "usuario_de_sistema", "carrera_registrada", "campus_registrado"
    )
    return render(request, "usuarios/listar_estudiantes.html", {"estudiantes": estudiantes})


@login_required
def registrar_estudiante(request):
    if request.method == "POST":
        formulario_usuario = FormularioUsuarioDeSistema(request.POST)
        formulario_perfil = FormularioPerfilEstudiante(request.POST)
        if formulario_usuario.is_valid() and formulario_perfil.is_valid():
            usuario = formulario_usuario.save(commit=False)
            usuario.set_password(formulario_usuario.cleaned_data["contrasena"])
            usuario.save()
            perfil = formulario_perfil.save(commit=False)
            perfil.usuario_de_sistema = usuario
            perfil.save()
            messages.success(request, "Estudiante registrado correctamente.")
            return redirect("listar_estudiantes")
    else:
        formulario_usuario = FormularioUsuarioDeSistema()
        formulario_perfil = FormularioPerfilEstudiante()
    return render(request, "usuarios/formulario_estudiante.html", {
        "formulario_usuario": formulario_usuario,
        "formulario_perfil": formulario_perfil,
        "titulo": "Registrar estudiante",
    })


@login_required
def listar_administrativos(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente.")
        return redirect("panel_principal")

    administrativos = PerfilAdministrativo.objects.filter(
        universidad=universidad_usuario
    ).select_related("usuario_de_sistema")
    
    return render(request, "usuarios/listar_administrativos.html", {"administrativos": administrativos})


@login_required
def registrar_administrativo(request):
    universidad_usuario = request.user.perfil_administrativo.universidad
    if not universidad_usuario:
        messages.warning(request, "La universidad no ha sido registrada actualmente.")
        return redirect("panel_principal")

    if request.method == "POST":
        formulario_usuario = FormularioUsuarioDeSistema(request.POST)
        formulario_perfil = FormularioPerfilAdministrativo(request.POST)

        if formulario_usuario.is_valid() and formulario_perfil.is_valid():
            usuario = formulario_usuario.save(commit=False)
            usuario.set_password(formulario_usuario.cleaned_data["contrasena"])
            usuario.save()
            
            perfil = formulario_perfil.save(commit=False)
            perfil.usuario_de_sistema = usuario
            perfil.universidad = universidad_usuario
            perfil.save()
            
            messages.success(request, "El usuario administrativo ha sido registrado correctamente.")
            return redirect("listar_administrativos")
    else:
        formulario_usuario = FormularioUsuarioDeSistema()
        formulario_perfil = FormularioPerfilAdministrativo()

    return render(request, "usuarios/formulario_administrativo.html", {
        "form_usuario": formulario_usuario,
        "form_perfil": formulario_perfil,
        "titulo": "Registrar perfil administrativo",
        "boton_texto": "Registrar",
    })


#Acciones sobre estudiantes
@login_required
def formalizar_matricula(request, estudiante_id):
    perfil = get_object_or_404(PerfilEstudiante, pk=estudiante_id)
    resultado = services.servicio_formalizar_matricula(perfil)
    if resultado:
        messages.success(request, f"Matrícula formalizada: {perfil.usuario_de_sistema.nombres}.")
    else:
        messages.error(request, "No se pudo formalizar la matrícula.")
    return redirect("listar_estudiantes")


@login_required
def solicitar_retiro(request, estudiante_id):
    perfil = get_object_or_404(PerfilEstudiante, pk=estudiante_id)
    resultado = services.servicio_solicitar_retiro(perfil)
    if resultado:
        messages.success(request, "Retiro solicitado correctamente.")
    else:
        messages.error(request, "No se pudo procesar el retiro.")
    return redirect("listar_estudiantes")


@login_required
def aprobar_retiro(request, estudiante_id):
    perfil = get_object_or_404(PerfilEstudiante, pk=estudiante_id)
    resultado = services.servicio_aprobar_retiro(perfil)
    if resultado:
        messages.success(request, "Retiro aprobado correctamente.")
    else:
        messages.error(request, "No se pudo aprobar el retiro.")
    return redirect("listar_estudiantes")


@login_required
def anular_matricula(request, estudiante_id):
    perfil = get_object_or_404(PerfilEstudiante, pk=estudiante_id)
    services.servicio_anular_matricula(perfil)
    messages.success(request, "Matrícula anulada correctamente.")
    return redirect("listar_estudiantes")


@login_required
def inhabilitar_docente(request, docente_id):
    perfil = get_object_or_404(PerfilDocente, pk=docente_id)
    services.servicio_inhabilitar_docente(perfil)
    messages.success(request, "Docente inhabilitado correctamente.")
    return redirect("listar_docentes")