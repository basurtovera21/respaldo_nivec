from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path("", views.iniciar_sesion, name="iniciar_sesion"),
    path("cerrar-sesion/", views.cerrar_sesion, name="cerrar_sesion"),
    
    path("panel/", views.panel_principal, name="panel_principal"), 
    path("mi-perfil/", views.modificar_datos_de_usuario, name="modificar_perfil"),

    # Paneles por rol
    path("panel/director-dan/", views.panel_director_dan, name="panel_director_dan"),
    path("panel/dan/", views.panel_dan, name="panel_dan"),
    path("panel/ua/", views.panel_ua, name="panel_ua"),
    path("panel/docente/", views.panel_docente, name="panel_docente"),
    path("panel/estudiante/", views.panel_estudiante, name="panel_estudiante"),
    path("panel/administrativo/", views.panel_administrativo, name="panel_administrativo"),
    
    # Docentes
    path("docentes/", views.listar_docentes, name="listar_docentes"),
    path("docentes/registrar/", views.registrar_docente, name="registrar_docente"),
    path("docentes/descargar-plantilla/", views.descargar_plantilla_docente, name="descargar_plantilla_docente"),
    path("docentes/modificar/<int:docente_id>/", views.modificar_docente, name="modificar_docente"),
    path("docentes/eliminar/<int:docente_id>/", views.eliminar_docente, name="eliminar_docente"),
    path("docentes/<int:docente_id>/inhabilitar/", views.inhabilitar_docente, name="inhabilitar_docente"),
    path("docentes/<int:docente_id>/habilitar/", views.habilitar_docente, name="habilitar_docente"),
    
    # Estudiantes
    path("estudiantes/", views.listar_estudiantes, name="listar_estudiantes"),
    path("estudiantes/registrar/", views.registrar_estudiante, name="registrar_estudiante"),
    path("estudiantes/descargar-plantilla/", views.descargar_plantilla_estudiante, name="descargar_plantilla_estudiante"),
    path("estudiantes/modificar/<int:estudiante_id>/", views.modificar_estudiante, name="modificar_estudiante"),
    path("estudiantes/eliminar/<int:estudiante_id>/", views.eliminar_estudiante, name="eliminar_estudiante"),
    path("estudiantes/<int:estudiante_id>/retiro/", views.solicitar_retiro, name="solicitar_retiro"),
    path("estudiantes/<int:estudiante_id>/anular/", views.anular_matricula, name="anular_matricula"),
    path("estudiantes/<int:estudiante_id>/matricular/", views.formalizar_matricula, name="formalizar_matricula"),
    
    # Administrativos
    path("administrativos/", views.listar_administrativos, name="listar_administrativos"),
    path("administrativos/registrar/", views.registrar_administrativo, name="registrar_administrativo"),
    path('administrativos/descargar-plantilla/', views.descargar_plantilla_administrativo, name='descargar_plantilla_administrativo'),
    path("administrativos/coordinadores-dan/", views.listar_coordinadores_dan, name="listar_coordinadores_dan"),
    path("administrativos/registrar-coordinador-dan/", views.registrar_coordinador_dan, name="registrar_coordinador_dan"),
    path('coordinador-dan/descargar-plantilla/', views.descargar_plantilla_coordinador_dan, name='descargar_plantilla_coordinador_dan'),
    path("administrativos/coordinadores-ua/", views.listar_coordinadores_ua, name="listar_coordinadores_ua"),
    path("administrativos/coordinadores-ua/registrar/", views.registrar_coordinador_ua, name="registrar_coordinador_ua"),
    path('coordinadores-ua/descargar-plantilla/', views.descargar_plantilla_coordinador_ua, name='descargar_plantilla_coordinador_ua'),
    path("administrativos/<int:admin_id>/modificar/", views.modificar_administrativo, name="modificar_administrativo"),
    path("administrativos/<int:admin_id>/eliminar/", views.eliminar_administrativo, name="eliminar_administrativo"),
]