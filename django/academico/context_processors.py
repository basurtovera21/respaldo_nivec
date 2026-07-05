"""
Context processor que inyecta los permisos basados en el estado del periodo
en TODAS las plantillas del proyecto automáticamente.

Cada template puede acceder directamente a variables como:
    {{ puede_modificar_campus }}
    {{ puede_eliminar_carrera }}
    {{ puede_registrar_malla }}
    etc.
"""

from academico.permisos import obtener_permisos_periodo


def permisos_periodo(request):
    """
    Inyecta todos los permisos del periodo en el contexto de cada request.
    Solo se ejecuta para usuarios autenticados con perfil administrativo.
    """
    if not request.user.is_authenticated:
        return {}

    # Obtener universidad del usuario
    perfil_admin = getattr(request.user, 'perfil_administrativo', None)
    if perfil_admin:
        universidad = perfil_admin.universidad
    else:
        perfil_docente = getattr(request.user, 'perfil_docente', None)
        if perfil_docente:
            universidad = perfil_docente.universidad
        else:
            return {}

    if not universidad:
        return {}

    permisos = obtener_permisos_periodo(universidad)
    return permisos
