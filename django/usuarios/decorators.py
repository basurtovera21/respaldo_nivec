from django.shortcuts import redirect
from functools import wraps


def universidad_requerida(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        perfil = request.user.perfil_administrativo
        if not perfil.universidad:
            return redirect('registrar_universidad')
        
        request.universidad = perfil.universidad
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view