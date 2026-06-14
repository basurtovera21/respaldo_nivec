# usuarios/utils.py
from django.db.models import Max
import re

def generar_identificador_siguiente(modelo, prefijo, nombre_campo):
    resultado_agregado = modelo.objects.filter(
        **{f"{nombre_campo}__startswith": prefijo}
    ).aggregate(Max(nombre_campo))

    identificador_maximo = resultado_agregado[f"{nombre_campo}__max"]

    if identificador_maximo:
        correlativo_actual = int(re.search(r'\d+', identificador_maximo).group())
        siguiente_correlativo = correlativo_actual + 1
    else:
        siguiente_correlativo = 1
        
    return f"{prefijo}{siguiente_correlativo:03d}"