from django.urls import path
from . import views

urlpatterns = [
    # Universidad
    path("universidad/detalle/", views.detalle_universidad, name="detalle_universidad"),
    path("universidad/registrar/", views.registrar_universidad, name="registrar_universidad"),
    path("universidad/editar/", views.modificar_universidad, name="modificar_universidad"),
    
    #Campus
    path("campus/", views.listar_campus, name="listar_campus"),
    path("campus/registrar/", views.registrar_campus, name="registrar_campus"),
    path("campus/editar/<int:campus_id>/", views.modificar_campus, name="modificar_campus"),
    path("campus/eliminar/<int:campus_id>/", views.eliminar_campus, name="eliminar_campus"),

    # Carrera
    path("carreras/", views.listar_carreras, name="listar_carreras"),
    path("carreras/registrar/", views.registrar_carrera, name="registrar_carrera"),
    path("carreras/editar/<int:carrera_id>/", views.modificar_carrera, name="modificar_carrera"),
    path("carreras/eliminar/<int:carrera_id>/", views.eliminar_carrera, name="eliminar_carrera"),
    
    #Periodo de nivelación
    path("periodos/", views.listar_periodos, name="listar_periodos"),
    path("periodos/registrar/", views.registrar_periodo, name="registrar_periodo"),
    path("periodos/editar/<int:periodo_id>/", views.modificar_periodo, name="modificar_periodo"),
    path("periodos/eliminar/<int:periodo_id>/", views.eliminar_periodo, name="eliminar_periodo"),
    path("periodos/<int:periodo_id>/iniciar/", views.iniciar_periodo, name="iniciar_periodo"),
    path("periodos/<int:periodo_id>/finalizar/", views.finalizar_periodo, name="finalizar_periodo"),

    #Estructura académica
    path("mallas/", views.listar_mallas, name="listar_mallas"),
    path("mallas/registrar/", views.registrar_malla, name="registrar_malla"),
    path("unidades/", views.listar_unidades, name="listar_unidades"),
    path("unidades/registrar/", views.registrar_unidad, name="registrar_unidad"),
    path("paralelos/", views.listar_paralelos, name="listar_paralelos"),
    path("paralelos/registrar/", views.registrar_paralelo, name="registrar_paralelo"),
    path("horarios/registrar/", views.registrar_horario, name="registrar_horario"),
    #Procesos académicos
    path("cohortes/", views.listar_cohortes, name="listar_cohortes"),
    path("cohortes/registrar/", views.registrar_cohorte, name="registrar_cohorte"),
    path("matriculas/registrar/", views.registrar_matricula, name="registrar_matricula"),
    path("consolidado/procesar/", views.procesar_mtn, name="procesar_mtn"),
    path("evaluaciones/", views.listar_evaluaciones, name="listar_evaluaciones"),
    path("evaluaciones/registrar/", views.registrar_evaluacion, name="registrar_evaluacion"),
    path("incidencias/", views.listar_incidencias, name="listar_incidencias"),
    path("incidencias/registrar/", views.registrar_incidencia, name="registrar_incidencia"),
    path("desempeno/registrar/", views.registrar_desempeno, name="registrar_desempeno"),
    #Distribución automática
    path("distribuir/<int:periodo_id>/", views.distribuir_estudiantes, name="distribuir_estudiantes"),
    #Informe
    path("informes/", views.listar_informes, name="listar_informes"),
    path("informes/registrar/", views.registrar_informe, name="registrar_informe"),
    path("informes/<int:informe_id>/emitir/", views.emitir_informe, name="emitir_informe"),
    path("informes/<int:informe_id>/exportar/", views.exportar_informe, name="exportar_informe"),
]