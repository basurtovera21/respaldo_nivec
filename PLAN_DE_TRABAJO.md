# PLAN DE TRABAJO — Transformación de estado_inicial a NIVEC

## Objetivo

Transformar el repositorio `estado_inicial` (capa POO pura) en el sistema completo
`respaldo_nivec` (Django + POO) de forma progresiva, dividido en 3 sprints con 5 integrantes.

## Equipo

| # | Rol | Responsabilidad principal |
|---|---|---|
| 1 | Líder / Integrador | Estructura, services de carga masiva, paralelos/horarios |
| 2 | Backend Usuarios | Modelos usuarios, autenticación, evaluaciones |
| 3 | Backend Académico | Modelos académicos, views entidades, MTN |
| 4 | POO / Mallas | Mejoras POO, views mallas/periodos, informes |
| 5 | Frontend / Permisos | Templates, views usuarios CRUD, permisos |

---

## Estrategia de Ramas (Git Flow)


```
main (estado_inicial actual — solo POO)
│
├── sprint-1/estructura-proyecto        ← Persona 1
├── sprint-1/modelos-usuarios           ← Persona 2
├── sprint-1/modelos-academico          ← Persona 3
├── sprint-1/poo-mejoras                ← Persona 4
├── sprint-1/templates-base             ← Persona 5
│
│   (merge a main en orden → Sprint 1 completo)
│
├── sprint-2/services-carga-masiva      ← Persona 1
├── sprint-2/autenticacion-paneles      ← Persona 2
├── sprint-2/views-entidades            ← Persona 3
├── sprint-2/views-mallas-periodos      ← Persona 4
├── sprint-2/views-usuarios-crud        ← Persona 5
│
│   (merge a main → Sprint 2 completo)
│
├── sprint-3/paralelos-horarios         ← Persona 1
├── sprint-3/evaluaciones               ← Persona 2
├── sprint-3/mtn-consolidado            ← Persona 3
├── sprint-3/informes-exportacion       ← Persona 4
├── sprint-3/permisos-estados           ← Persona 5
│
│   (merge a main → Sprint 3 = PROYECTO COMPLETO)
```

---

## Reglas del Equipo

1. **NUNCA** pushear directo a `main`
2. Siempre crear Pull Request desde tu rama
3. Al menos 1 compañero revisa antes de mergear
4. Si hay conflicto de merge, el autor de la PR lo resuelve
5. Después de cada Sprint, **todos** hacen `git pull origin main`
6. Commits en español con formato: `feat(modulo): descripción`

---


## Comandos Git para cada integrante

```bash
# ═══ INICIO DE CADA SPRINT ═══
git checkout main
git pull origin main
git checkout -b sprint-X/nombre-de-mi-tarea

# ═══ DURANTE EL TRABAJO (guardar progreso) ═══
git add .
git commit -m "feat(modulo): lo que avancé"

# ═══ AL TERMINAR MI TAREA ═══
git push origin sprint-X/nombre-de-mi-tarea
# → Ir a GitHub y crear Pull Request hacia main

# ═══ DESPUÉS DEL MERGE DEL SPRINT ═══
git checkout main
git pull origin main
# → Listo para el siguiente sprint
```

---

## SPRINT 1 — Base del Sistema

**Objetivo:** Tener la estructura Django funcional con modelos, migraciones y templates base.
**Duración sugerida:** 3-4 días

### Orden de merge (IMPORTANTE):
1. Persona 1 → `sprint-1/estructura-proyecto` (todos dependen de esto)
2. Persona 4 → `sprint-1/poo-mejoras`
3. Persona 2 → `sprint-1/modelos-usuarios`
4. Persona 3 → `sprint-1/modelos-academico`
5. Persona 5 → `sprint-1/templates-base`

---


### Persona 1 — Estructura del proyecto Django

**Rama:** `sprint-1/estructura-proyecto`

**Archivos a crear:**
```
django/
├── manage.py
├── nivec/
│   ├── __init__.py
│   ├── settings.py          ← Configurar SQLite, apps, templates, static
│   ├── urls.py              ← URLs raíz (incluir academico/ y usuarios/)
│   ├── wsgi.py
│   └── asgi.py
├── academico/
│   ├── __init__.py
│   └── apps.py
├── usuarios/
│   ├── __init__.py
│   └── apps.py
├── templates/               ← Carpeta vacía (para Persona 5)
├── static/                  ← Carpeta vacía
.env                         ← SECRET_KEY (sin DATABASE_URL = SQLite)
.gitignore                   ← db.sqlite3, __pycache__, venv/, etc.
requirements.txt             ← django, openpyxl, python-dotenv, dj-database-url
```

**Detalle de settings.py:**
- `AUTH_USER_MODEL = "usuarios.UsuarioDeSistema"`
- Base de datos: SQLite por defecto, PostgreSQL si hay DATABASE_URL
- `LANGUAGE_CODE = "es"`, `TIME_ZONE = "America/Guayaquil"`
- INSTALLED_APPS: `usuarios`, `academico`

**Verificación:** `python manage.py check` debe pasar sin errores.

---


### Persona 2 — Modelos de Usuarios

**Rama:** `sprint-1/modelos-usuarios`

**Archivos a crear/modificar:**
```
django/usuarios/
├── models.py       ← UsuarioDeSistema, PerfilDocente, PerfilEstudiante, PerfilAdministrativo
├── admin.py        ← Registrar modelos en el admin de Django
└── urls.py         ← Archivo vacío con urlpatterns = [] (se llena en Sprint 2)
```

**Modelos a implementar:**

1. **CreadorDeUsuarios** (BaseUserManager)
   - `create_user(correo_institucional, password, **kwargs)`
   - `create_superuser(correo_institucional, password, **kwargs)`

2. **UsuarioDeSistema** (AbstractBaseUser, PermissionsMixin)
   - Campos: tipo_de_identificacion, identificacion, nombres, apellidos,
     correo_institucional, fecha_de_nacimiento, sexo, etnia,
     porcentaje_de_discapacidad, celular, direccion, estado_de_usuario
   - USERNAME_FIELD = "correo_institucional"

3. **PerfilDocente** (OneToOne con UsuarioDeSistema)
   - Campos: universidad (FK), identificador_institucional, tipo_de_vinculacion,
     tiempo_de_dedicacion, estado_de_vinculacion, carga_horaria_maxima, jornadas (JSON)

4. **PerfilEstudiante** (OneToOne con UsuarioDeSistema)
   - Campos: identificador_institucional, numero_de_matricula, jornada,
     registro_de_cupo, carrera_registrada (FK), campus_registrado (FK),
     estado_de_matricula, periodo_de_nivelacion (FK)

5. **PerfilAdministrativo** (OneToOne con UsuarioDeSistema)
   - Campos: universidad (FK), identificador_administrativo, perfil_administrativo,
     identificador_coordinador_dan, identificador_coordinador_ua,
     unidad_academica, carrera_asignada (FK)

**Nota:** Los ForeignKey a `academico.Universidad`, `academico.Carrera`, etc.
se declaran como strings: `models.ForeignKey('academico.Universidad', ...)`

**Verificación:** `python manage.py makemigrations usuarios` debe generar migraciones.

---


### Persona 3 — Modelos Académicos

**Rama:** `sprint-1/modelos-academico`

**Archivos a crear/modificar:**
```
django/academico/
├── models.py       ← 14 modelos del dominio académico
├── admin.py        ← Registrar modelos en el admin
└── urls.py         ← Archivo vacío con urlpatterns = [] (se llena en Sprint 2)
```

**Modelos a implementar (en este orden por dependencias FK):**

1. **Universidad** — nombre, abreviatura, codigo_sniese, direccion_matriz, identificador_visual
2. **Campus** — FK(Universidad), codigo_de_campus, nombre, direccion_fisica, provincia
3. **Carrera** — FK(Campus), codigo_de_carrera, nombre, vigencia_sniese
4. **MallaCurricular** — FK(Carrera), codigo_de_malla, nombre, version_de_malla, estado, total_horas
5. **UnidadCurricular** — FK(MallaCurricular), codigo_de_unidad, nombre, horas_*, criterio_aprobacion
6. **PeriodoDeNivelacion** — FK(Universidad), codigo_periodo, anio, periodo, fechas, modalidad, estado
7. **Paralelo** — FK(PeriodoDeNivelacion), FK(UnidadCurricular), codigo, nombre, jornada, modalidad, capacidad, FK(docente)
8. **Horario** — FK(Paralelo), dia_semana, hora_inicio, hora_fin, espacio
9. **CohorteDeMatricula** — FK(Periodo), FK(Carrera), codigo, nombre, fecha_cierre, tipo, totales
10. **MatriculaParalelo** — FK(Estudiante), FK(Paralelo), FK(Cohorte), fecha_registro
11. **ConsolidadoAcademico** — OneToOne(Periodo), fecha_corte, totales
12. **EvaluacionAcademica** — FK(Estudiante), FK(UC), calificaciones, nota_final, estado, observacion
13. **IncidenciaAcademica** — codigo, FK(Docente), descripcion, fecha, FK(Administrativo)
14. **EvaluacionDeDesempeno** — FK(Docente), FK(Periodo), porcentajes, puntaje_final
15. **InformeGeneral** — FK(Periodo), codigo, tipo, estado, fecha_emision, M2M(Cohortes)

**Función auxiliar:** `cambiar_enum_a_choices(enum_clase)` para convertir enums POO en choices Django.

**Verificación:** `python manage.py makemigrations academico` debe generar migraciones.
Luego `python manage.py migrate` debe crear todas las tablas.

---


### Persona 4 — Mejoras a la capa POO

**Rama:** `sprint-1/poo-mejoras`

**Objetivo:** Mejorar las clases de `estado_inicial/clases/` para que sirvan a Django.
Mover la carpeta `clases/` a `poo/clases/` y adaptar imports.

**Cambios a realizar:**

1. **Reestructurar carpeta:**
   ```
   clases/ → poo/clases/   (agregar poo/__init__.py vacío)
   ```
   Actualizar TODOS los imports de `clases.xxx` a `poo.clases.xxx`

2. **Agregar encapsulación** (properties) a las entidades principales:
   - `universidad.py` — validar_datos_de_registro(), recuperar_informacion_institucional()
   - `campus.py` — validar_datos_de_registro(), validar_datos_de_carga_masiva()
   - `carrera.py` — esta_activa(), validar_datos_de_registro()
   - `unidad_curricular.py` — validar_datos_de_registro(), validar_horas(), validar_criterios()

3. **Agregar métodos que Django necesita:**
   - `UnidadCurricular.calcular_horas_sincronicas_semanales(semanas)`
   - `PeriodoDeNivelacion.esta_en_planificacion()`, `permite_gestion_matriculas()`
   - `Paralelo.generar_nombre_por_indice(indice)` (staticmethod)
   - `MallaCurricular.validar_datos_de_registro()`

4. **Agregar `franja_horaria.py`** — módulo de configuración de franjas horarias

5. **Fix:** Cambiar `IAsignableAHorario | None` a `Optional[IAsignableAHorario]` (Python 3.9)

**Verificación:** `python -c "from poo.clases.universidad import Universidad; print('OK')"` debe funcionar.

---


### Persona 5 — Templates Base y CSS

**Rama:** `sprint-1/templates-base`

**Archivos a crear:**
```
django/templates/
├── base.html                ← Template padre (navbar, messages, block contenido)
├── base_formulario.html     ← Extiende base.html (título + formulario + botones)
├── base_listar.html         ← Extiende base.html (título + tabla + acciones)
django/static/
├── css/
│   └── estilos.css          ← Estilos generales del sistema
```

**Contenido de base.html:**
- Estructura HTML5 con meta viewport
- Navbar con navegación condicional por rol (usar `{{ request.user }}`)
- Bloque de mensajes Django (`{% for message in messages %}`)
- Block `contenido` para que las páginas hijas lo llenen
- Link a estilos.css

**Contenido de base_formulario.html:**
- Extiende `base.html`
- Muestra `{{ titulo }}`
- Renderiza `{{ formulario }}` con errores
- Botones Guardar y Cancelar

**Contenido de base_listar.html:**
- Extiende `base.html`
- Muestra `{{ titulo }}`
- Tabla con datos iterables
- Botón de "Registrar nuevo"

**Verificación:** Abrir el servidor (`runserver`) y ver que `base.html` carga sin errores.

---

## SPRINT 2 — Funcionalidades CRUD

**Objetivo:** Todas las entidades tienen vistas para crear, listar, editar y eliminar.
**Duración sugerida:** 5-7 días
**Prerequisito:** Sprint 1 mergeado completamente.

### Orden de merge: Cualquier orden (son independientes entre sí)

---


### Persona 1 — Services de Carga Masiva

**Rama:** `sprint-2/services-carga-masiva`

**Archivos a crear:**
```
django/academico/services.py   ← Funciones de carga masiva desde Excel
django/usuarios/services.py    ← Funciones de carga masiva de usuarios
django/usuarios/utils.py       ← generar_identificador_siguiente, roles, decorador requiere_perfil
```

**Funciones a implementar en academico/services.py:**
- `normalizar_texto(texto)` — normalizar para comparaciones
- `obtener_enum_flexible(enum_class, valor_sucio)` — match flexible de enums
- `servicio_campus_registrar_masivo_desde_excel(archivo, universidad)`
- `servicio_carrera_registrar_masivo_desde_excel(archivo, universidad)`
- `servicio_malla_registrar_masivo_desde_excel(archivo, universidad)`
- `servicio_unidad_registrar_masivo_desde_excel(archivo, universidad)`

**Funciones a implementar en usuarios/services.py:**
- `servicio_iniciar_sesion(request, correo, contrasena)`
- `servicio_cerrar_sesion(request)`
- `servicio_administrativo_registrar_masivo_desde_excel(archivo, universidad)`
- `servicio_coordinador_dan_registrar_masivo_desde_excel(archivo, universidad)`
- `servicio_coordinador_ua_registrar_masivo_desde_excel(archivo, universidad)`
- `servicio_docente_registrar_masivo_desde_excel(archivo, universidad)`
- `servicio_estudiante_registrar_masivo_desde_excel(archivo, universidad)`

**Funciones a implementar en usuarios/utils.py:**
- `generar_identificador_siguiente(modelo, prefijo, campo)` — genera CAM001, CAR002, etc.
- Constantes: ROL_RECTOR, ROL_DOCENTE, ROL_ESTUDIANTE, etc.
- `obtener_rol_usuario(usuario)` — determina el rol
- `requiere_perfil(*roles)` — decorador de acceso

**Patrón:** Cada servicio de carga masiva retorna `{"exitosos": int, "advertencias": [], "error": str|None}`

---

### Persona 2 — Autenticación y Paneles

**Rama:** `sprint-2/autenticacion-paneles`

**Archivos a crear:**
```
django/usuarios/views/
├── __init__.py
├── v_autenticacion.py     ← Login, logout, panel_principal, paneles por rol
django/usuarios/urls.py    ← Rutas de autenticación y paneles
django/templates/
├── autenticacion/
│   └── iniciar_sesion.html
├── administrativo/
│   ├── panel_director_dan.html
│   ├── panel_dan.html
│   └── panel_ua.html
├── docente/
│   └── panel_docente.html
├── estudiante/
│   └── panel_estudiante.html
```

**Vistas a implementar:**
- `iniciar_sesion(request)` — formulario de login, usa `servicio_iniciar_sesion`
- `cerrar_sesion(request)` — logout y redirect
- `panel_principal(request)` — redirige según rol
- `panel_director_dan(request)` — dashboard del director
- `panel_dan(request)` — dashboard coordinador DAN
- `panel_ua(request)` — dashboard coordinador UA
- `panel_docente(request)` — dashboard docente
- `panel_estudiante(request)` — dashboard estudiante

---


### Persona 3 — Views Entidades (Universidad, Campus, Carreras)

**Rama:** `sprint-2/views-entidades`

**Archivos a crear:**
```
django/academico/views/
├── __init__.py
├── v_universidad.py       ← detalle, registrar, modificar
├── v_campus.py            ← listar, registrar, modificar, eliminar, carga masiva
├── v_carrera.py           ← listar, registrar, modificar, eliminar, carga masiva
django/academico/forms.py  ← FormularioUniversidad, FormularioCampus, FormularioCarrera
django/academico/urls.py   ← Rutas de estas entidades
django/templates/entidades/
├── detalle_universidad.html
├── formulario_universidad.html
├── formulario_campus.html
├── formulario_carrera.html
├── listar_campus.html
├── listar_carreras.html
```

**Vistas por entidad:**
- Universidad: `detalle_universidad`, `registrar_universidad`, `modificar_universidad`
- Campus: `listar_campus`, `registrar_campus`, `modificar_campus`, `eliminar_campus`
- Carrera: `listar_carreras`, `registrar_carrera`, `modificar_carrera`, `eliminar_carrera`

**Formularios (forms.py):**
- Cada formulario usa la clase POO para validar (ej: `CarreraBase.esta_activa()`)
- Formularios heredan de `forms.ModelForm`

---

### Persona 4 — Views Mallas, Periodos y Unidades Curriculares

**Rama:** `sprint-2/views-mallas-periodos`

**Archivos a crear:**
```
django/academico/views/
├── v_malla_curricular.py     ← listar, registrar, modificar, eliminar, clonar, cambiar estado
├── v_unidad_curricular.py    ← listar, registrar, modificar, eliminar, carga masiva
├── v_periodo_de_nivelacion.py ← listar, registrar, modificar, eliminar, iniciar, finalizar
django/academico/forms.py     ← Agregar FormularioMallaCurricular, FormularioUnidadCurricular, FormularioPeriodoDeNivelacion
django/templates/academico/
├── listar_mallas.html
├── formulario_malla.html
├── listar_unidades.html
├── formulario_unidad.html
├── listar_periodos.html
├── formulario_periodo.html
```

**Funcionalidades especiales:**
- Malla: clonar (usa Patrón Prototype de POO), cambiar estado (activar/inactivar/histórica)
- Periodo: iniciar (cambia estado), pasar a evaluación, finalizar
- Unidad: validación de distribución de horas vía POO

---


### Persona 5 — Views CRUD de Usuarios

**Rama:** `sprint-2/views-usuarios-crud`

**Archivos a crear:**
```
django/usuarios/views/
├── __init__.py
├── v_docentes.py              ← listar, registrar, modificar, eliminar, inhabilitar/habilitar
├── v_estudiantes.py           ← listar, registrar, modificar, eliminar, retiro, anular, matricular
├── v_administrativos.py       ← listar, registrar, modificar, eliminar
├── v_coordinadores_dan.py     ← listar, registrar
├── v_coordinadores_ua.py      ← listar, registrar
├── v_perfil.py                ← modificar datos del perfil propio
django/usuarios/forms.py       ← Todos los formularios de usuarios
django/templates/usuarios/
├── listar_docentes.html
├── formulario_docente.html
├── listar_estudiantes.html
├── formulario_estudiante.html
├── listar_administrativos.html
├── formulario_administrativo.html
├── listar_coordinadores_dan.html
├── listar_coordinadores_ua.html
├── formulario_perfil.html
```

**Formularios a implementar:**
- FormularioUsuarioDeSistema (registrar)
- FormularioModificarUsuarioDeSistema (editar con contraseña opcional)
- FormularioPerfilEstudiante
- FormularioRegistrarDocente (con checkboxes de jornadas)
- FormularioPerfilAdministrativo
- FormularioRegistrarCoordinadorDAN
- FormularioRegistrarCoordinadorUA

**Nota:** Usar decorador `@requiere_perfil(ROL_DIRECTOR_DAN, ...)` para control de acceso.

---

## SPRINT 3 — Funcionalidades Avanzadas

**Objetivo:** Sistema completo con paralelos, horarios, evaluaciones, informes y permisos.
**Duración sugerida:** 7-10 días
**Prerequisito:** Sprint 2 mergeado completamente.

### Orden de merge: Cualquier orden (son independientes)

---


### Persona 1 — Paralelos y Horarios

**Rama:** `sprint-3/paralelos-horarios`

**Archivos a crear:**
```
django/academico/views/
├── v_paralelo.py          ← listar, generar, detalle, eliminar, mover/retirar/agregar estudiante
├── v_horario.py           ← listar, registrar, editar, eliminar, generar sugerido, matriz
├── v_asignacion_docente.py ← asignar/quitar docente de paralelo
```

**Services a agregar en academico/services.py:**
- `servicio_generar_paralelos(periodo, capacidad)` — distribución automática
- `servicio_mover_estudiante(estudiante, paralelo_destino)`
- `servicio_retirar_estudiante_de_paralelo(estudiante, paralelo)`
- `servicio_agregar_estudiante_a_paralelo(estudiante, paralelo)`
- `servicio_registrar_horario(paralelo, dia, inicio, fin, espacio)`
- `servicio_editar_horario(horario, dia, inicio, fin, espacio)`
- `servicio_generar_horario_sugerido(paralelo)`
- `servicio_asignar_docente(paralelo, docente)`
- `servicio_quitar_docente(paralelo)`

**Usa:** Facade (CentroDeOperacionAcademica), Distribuidor, Paralelo POO, franja_horaria

---

### Persona 2 — Evaluaciones Académicas

**Rama:** `sprint-3/evaluaciones`

**Archivos a crear:**
```
django/academico/views/
├── v_evaluacion.py        ← listar por paralelo, cargar desde Excel, detalle, editar, revisión, formalizar
```

**Services a agregar en academico/services.py:**
- `servicio_registrar_evaluacion_academica(evaluacion)` — usa Chain of Responsibility POO
- `servicio_cargar_calificaciones_desde_excel(archivo, paralelo, unidad, periodo)`
- `servicio_pasar_a_revision(paralelo)`
- `servicio_formalizar_evaluaciones(paralelo)`

**Flujo de estados:** Borrador → En revisión → Formalizado
- Docente carga calificaciones (Borrador)
- Docente pasa a revisión
- Coordinador UA formaliza

**Usa:** EvaluacionAcademica POO (Chain of Responsibility para calcular aprobación)

---

### Persona 3 — MTN y Consolidado Académico

**Rama:** `sprint-3/mtn-consolidado`

**Archivos a crear:**
```
django/academico/views/
├── v_mtn.py              ← procesar MTN, descargar plantilla, listar consolidados
```

**Services a agregar en academico/services.py:**
- `servicio_procesar_mtn(archivo, periodo)` — carga masiva de estudiantes + consolidado

**Funcionalidades:**
- Subir archivo Excel con la Matriz de Tercer Nivel
- Validar con DepuradorDeSincronizacion + CriterioCedulaFormato
- Crear estudiantes y generar consolidado académico
- Mostrar estadísticas (registros válidos vs observados)

**Usa:** DepuradorDeSincronizacion, ConsolidadoAcademico POO

---


### Persona 4 — Informes y Exportación

**Rama:** `sprint-3/informes-exportacion`

**Archivos a crear:**
```
django/academico/views/
├── v_procesos_academicos.py   ← listar informes, registrar, emitir, exportar, cohortes
```

**Services a agregar en academico/services.py:**
- `servicio_generar_informe_general(periodo)` — estadísticas por carrera
- `servicio_exportar_informe(informe, formato)` — genera Excel o TXT

**Funcionalidades:**
- Informe general: aprobados/reprobados/retirados por carrera
- Exportar a Excel (openpyxl) y TXT
- Emitir informe (cambia estado vía POO InformeGeneral)
- Gestión de cohortes de matrícula

**Usa:** ProcesadorDeInforme POO, InformeGeneral POO, Facade

---

### Persona 5 — Sistema de Permisos por Estado

**Rama:** `sprint-3/permisos-estados`

**Archivos a crear:**
```
django/academico/permisos.py            ← obtener_permisos_periodo(universidad)
django/academico/context_processors.py  ← inyectar permisos en todas las templates
```

**Funcionalidades:**

1. **permisos.py** — Función que retorna un diccionario con ~40 permisos booleanos:
   ```python
   permisos = obtener_permisos_periodo(universidad)
   # permisos["puede_registrar_campus"] → True/False
   # permisos["puede_gestionar_calificaciones"] → True/False
   ```

2. **context_processors.py** — Se agrega en settings.py, inyecta permisos en CADA template:
   ```html
   {% if puede_registrar_campus %}
       <a href="{% url 'registrar_campus' %}">Registrar</a>
   {% endif %}
   ```

3. **Integrar en templates existentes** — Agregar condicionales `{% if puede_X %}` en:
   - Botones de registrar/editar/eliminar
   - Menús de navegación
   - Acciones de paralelos/horarios/evaluaciones

**Estados del periodo y qué permiten:**
| Estado | Registrar estructura | Gestionar estudiantes | Horarios | Calificaciones |
|---|---|---|---|---|
| Sin periodo | ✅ | ✅ | ❌ | ❌ |
| Planificación | ✅ | ✅ | ✅ | ❌ |
| En curso | ❌ | ✅ | ❌ | ❌ |
| Evaluación | ❌ | ❌ | ❌ | ✅ |
| Cerrado | ❌ | ❌ | ❌ | ❌ |

---


## Estructura Final del Proyecto

```
respaldo_nivec/
├── .env                              ← Configuración (SQLite por defecto)
├── .gitignore
├── requirements.txt
├── PLAN_DE_TRABAJO.md
├── README.md
│
├── poo/                              ← Capa de dominio (lógica pura, sin Django)
│   └── clases/
│       ├── enums/                    ← 18 enumeraciones
│       ├── interfaces/               ← 9 interfaces abstractas
│       ├── criterios_filtro/         ← Strategy para validación
│       ├── servicios/                ← Facade, Distribuidor, Procesador, etc.
│       ├── usuarios/                 ← Docente, Estudiante, Administrativo
│       ├── universidad.py
│       ├── campus.py
│       ├── carrera.py
│       ├── malla_curricular.py
│       ├── unidad_curricular.py
│       ├── periodo_de_nivelacion.py
│       ├── paralelo.py
│       ├── horario.py
│       ├── evaluacion_academica.py
│       ├── cohorte_de_matricula.py
│       ├── consolidado_academico.py
│       ├── informe_general.py
│       └── franja_horaria.py
│
└── django/                           ← Capa web (Django)
    ├── manage.py
    ├── nivec/                        ← Configuración del proyecto
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    │
    ├── academico/                    ← App de gestión académica
    │   ├── models.py                ← 14 modelos
    │   ├── forms.py                 ← Formularios con validación POO
    │   ├── services.py              ← Orquestador (ORM + POO)
    │   ├── permisos.py              ← Sistema de permisos por estado
    │   ├── context_processors.py    ← Inyectar permisos en templates
    │   ├── urls.py                  ← ~90 rutas
    │   ├── admin.py                 ← Panel de administración
    │   └── views/                   ← 12 módulos de vistas
    │
    ├── usuarios/                     ← App de gestión de usuarios
    │   ├── models.py                ← 4 modelos (User + 3 perfiles)
    │   ├── forms.py                 ← Formularios de usuarios
    │   ├── services.py              ← Auth + carga masiva
    │   ├── utils.py                 ← Roles y decoradores
    │   ├── urls.py                  ← ~50 rutas
    │   ├── admin.py
    │   └── views/                   ← 7 módulos de vistas
    │
    ├── templates/                    ← Templates HTML
    │   ├── base.html
    │   ├── base_formulario.html
    │   ├── base_listar.html
    │   ├── autenticacion/
    │   ├── administrativo/
    │   ├── docente/
    │   ├── estudiante/
    │   ├── entidades/
    │   ├── academico/
    │   └── usuarios/
    │
    ├── static/                       ← CSS
    └── media/                        ← Archivos subidos
```

---

## Cómo ejecutar el proyecto (para presentación)

```bash
# 1. Clonar
git clone https://github.com/basurtovera21/estado_inicial.git
cd estado_inicial

# 2. Instalar dependencias
pip install django openpyxl python-dotenv dj-database-url

# 3. Crear base de datos (SQLite automática)
cd django
python manage.py migrate

# 4. Crear usuario administrador
python manage.py createsuperuser

# 5. Ejecutar
python manage.py runserver

# Abrir: http://127.0.0.1:8000/
```

---

## Patrones de Diseño Implementados

| Patrón | Ubicación | Uso |
|---|---|---|
| **Facade** | `centro_de_operacion_academica.py` | Punto de entrada unificado a la POO |
| **Prototype** | `malla_curricular.py` → `clonar()` | Clonar mallas con sus unidades |
| **Chain of Responsibility** | `manejadores_de_aprobacion.py` | Verificar aprobación académica |
| **Observer** | `i_sujeto_de_evaluacion.py` | Notificar cambios de estado |
| **Strategy** | `i_criterio_filtro.py`, `i_estrategia_de_evaluacion.py` | Validación y evaluación intercambiable |

## Principios SOLID

| Principio | Ejemplo |
|---|---|
| **SRP** | Cada clase tiene una sola responsabilidad |
| **OCP** | Nuevos manejadores de aprobación sin modificar los existentes |
| **LSP** | Todos los manejadores son intercambiables |
| **ISP** | IUnidadEvaluable solo exige 2 métodos |
| **DIP** | services.py depende de abstracciones POO, no de implementaciones |
