from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path("", views.iniciar_sesion, name="iniciar_sesion"),
    path("cerrar-sesion/", views.cerrar_sesion, name="cerrar_sesion"),
    path("sin-perfil/", views.panel_sin_perfil, name="sin_perfil"),
    
    path("panel/", views.panel_principal, name="panel_principal"), 

    # Paneles por rol
    path("panel/director-dan/", views.panel_director_dan, name="panel_director_dan"),
    path("panel/dan/", views.panel_dan, name="panel_dan"),
    path("panel/coordinador-ua/", views.panel_coordinador_ua, name="panel_ua"),
    path("panel/docente/", views.panel_docente, name="panel_docente"),
    path("panel/estudiante/", views.panel_estudiante, name="panel_estudiante"),
    path("panel/administrativo/", views.panel_administrativo, name="panel_administrativo"),

    # Usuarios
    path("usuarios/", views.listar_usuarios, name="listar_usuarios"),
    path("usuarios/registrar/", views.registrar_usuario, name="registrar_usuario"),
    path("docentes/", views.listar_docentes, name="listar_docentes"),
    path("docentes/registrar/", views.registrar_docente, name="registrar_docente"),
    path("estudiantes/", views.listar_estudiantes, name="listar_estudiantes"),
    path("estudiantes/registrar/", views.registrar_estudiante, name="registrar_estudiante"),
    path("administrativos/", views.listar_administrativos, name="listar_administrativos"),
    path("administrativos/registrar/", views.registrar_administrativo, name="registrar_administrativo"),
    
    path("estudiantes/<int:estudiante_id>/formalizar/", views.formalizar_matricula, name="formalizar_matricula"),
    path("estudiantes/<int:estudiante_id>/retiro/", views.solicitar_retiro, name="solicitar_retiro"),
    path("estudiantes/<int:estudiante_id>/aprobar-retiro/", views.aprobar_retiro, name="aprobar_retiro"),
    path("estudiantes/<int:estudiante_id>/anular/", views.anular_matricula, name="anular_matricula"),
    path("docentes/<int:docente_id>/inhabilitar/", views.inhabilitar_docente, name="inhabilitar_docente"),
]