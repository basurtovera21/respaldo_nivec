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
    path("campus/descargar-plantilla/", views.descargar_plantilla_campus, name="descargar_plantilla_campus"),

    # Carrera
    path("carreras/", views.listar_carreras, name="listar_carreras"),
    path("carreras/registrar/", views.registrar_carrera, name="registrar_carrera"),
    path("carreras/editar/<int:carrera_id>/", views.modificar_carrera, name="modificar_carrera"),
    path("carreras/eliminar/<int:carrera_id>/", views.eliminar_carrera, name="eliminar_carrera"),
    path("carrera/descargar-plantilla/", views.descargar_plantilla_carrera, name="descargar_plantilla_carrera"),
    
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
    path("mallas/editar/<int:malla_id>/", views.modificar_malla, name="modificar_malla"),
    path("mallas/eliminar/<int:malla_id>/", views.eliminar_malla, name="eliminar_malla"),
    path("mallas/clonar/<int:malla_id>/", views.clonar_malla, name="clonar_malla"),
    path("mallas/<int:malla_id>/estado/<str:accion>/", views.cambiar_estado_malla, name="cambiar_estado_malla"),
    path("mallas/descargar-plantilla/", views.descargar_plantilla_malla, name="descargar_plantilla_malla"),
    path("mallas/<int:malla_id>/unidades/", views.listar_unidades_de_malla, name="listar_unidades_de_malla"),

    path("unidades/", views.listar_unidades, name="listar_unidades"),
    path("unidades/registrar/", views.registrar_unidad, name="registrar_unidad"),
    path("unidades/editar/<int:unidad_id>/", views.modificar_unidad, name="modificar_unidad"),
    path("unidades/eliminar/<int:unidad_id>/", views.eliminar_unidad, name="eliminar_unidad"),
    path("unidades/descargar-plantilla/", views.descargar_plantilla_unidad, name="descargar_plantilla_unidad"),
    path("mallas/<int:malla_id>/unidades/", views.listar_unidades_de_malla, name="listar_unidades_de_malla"),
    
    path("paralelos/", views.listar_paralelos, name="listar_paralelos"),
    path("paralelos/generar/", views.generar_paralelos, name="generar_paralelos"),
    path("paralelos/<int:paralelo_id>/detalle/", views.detalle_paralelo, name="detalle_paralelo"),
    path("paralelos/eliminar/<int:paralelo_id>/", views.eliminar_paralelo, name="eliminar_paralelo"),
    path("paralelos/<int:paralelo_id>/estudiantes/", views.listar_estudiantes_paralelo, name="listar_estudiantes_paralelo"),
    path("paralelos/<int:paralelo_id>/mover-estudiante/", views.mover_estudiante, name="mover_estudiante"),
    path("paralelos/<int:paralelo_id>/retirar-estudiante/", views.retirar_estudiante, name="retirar_estudiante"),
    path("paralelos/<int:paralelo_id>/agregar-estudiante/", views.agregar_estudiante, name="agregar_estudiante"),
    path("paralelos/<int:paralelo_id>/horarios/", views.listar_horarios_paralelo, name="listar_horarios_paralelo"),
    path("paralelos/<int:paralelo_id>/horarios/registrar/", views.registrar_horario, name="registrar_horario"),
    path("horarios/<int:horario_id>/eliminar/", views.eliminar_horario, name="eliminar_horario"),
    path("horarios/matriz/", views.matriz_horarios, name="matriz_horarios"),
    path("paralelos/<int:paralelo_id>/docente/", views.asignar_docente_paralelo, name="asignar_docente_paralelo"),
    #Procesos académicos
    path("cohortes/", views.listar_cohortes, name="listar_cohortes"),
    path("cohortes/registrar/", views.registrar_cohorte, name="registrar_cohorte"),
    path("matriculas/registrar/", views.registrar_matricula, name="registrar_matricula"),
    path("consolidado/procesar/", views.procesar_mtn, name="procesar_mtn"),
    path("mtn/descargar-plantilla/", views.descargar_plantilla_mtn, name="descargar_plantilla_mtn"),
    path("consolidados/", views.listar_consolidados, name="listar_consolidados"),
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