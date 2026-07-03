from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from usuarios.forms import FormularioModificarUsuarioDeSistema

@login_required
def modificar_datos_de_usuario(request):
    usuario_actual = request.user
    if request.method == "POST":
        formulario = FormularioModificarUsuarioDeSistema(request.POST, instance=usuario_actual)
        if 'estado_de_usuario' in formulario.fields:
            del formulario.fields['estado_de_usuario']

        for campo in ["tipo_de_identificacion", "identificacion", "correo_institucional"]:
            if campo in formulario.fields:
                formulario.fields[campo].disabled = True
        
        if formulario.is_valid():
            usuario_modificado = formulario.save(commit=False)
            nueva_contrasena = formulario.cleaned_data.get("contrasena")
            
            if nueva_contrasena:
                usuario_modificado.set_password(nueva_contrasena)
                
            usuario_modificado.save()
            
            if nueva_contrasena:
                update_session_auth_hash(request, usuario_modificado)
                
            messages.success(request, "La información ha sido actualizada correctamente")
            return redirect("panel_principal")
    else:
        formulario = FormularioModificarUsuarioDeSistema(instance=usuario_actual)

        if 'estado_de_usuario' in formulario.fields:
            del formulario.fields['estado_de_usuario']

        for campo in ["tipo_de_identificacion", "identificacion", "correo_institucional"]:
            if campo in formulario.fields:
                formulario.fields[campo].disabled = True
                formulario.fields[campo].widget.attrs.update({
                    'style': 'background-color: #f5f5f7; color: #86868b; pointer-events: none;',
                    'readonly': True
                })
                
    return render(request, "usuarios/formulario_perfil.html", {
        "formulario": formulario,
        "titulo_pagina": "NIVEC",
        "titulo": f"{usuario_actual.nombres} {usuario_actual.apellidos}",
        "boton_texto": "Actualizar",
        "url_cancelar": "panel_principal"
    })