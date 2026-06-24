# IMPORTANTE: views_old se importa PRIMERO para que las vistas modulares
# (definidas abajo) sobreescriban cualquier función con el mismo nombre.
# Las funciones que solo existen en views_old (paralelos, cohortes, MTN,
# evaluaciones, informes, etc.) siguen disponibles hasta que se migren.
from academico.views_old import *

from .v_universidad import *
from .v_campus import *
from .v_carrera import *
from .v_periodo_de_nivelacion import *
from .v_malla_curricular import *
from .v_unidad_curricular import *
