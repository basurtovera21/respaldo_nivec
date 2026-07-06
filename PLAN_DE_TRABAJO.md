# PLAN DE TRABAJO — Transformación de estado_inicial a NIVEC

## Objetivo

Transformar progresivamente `estado_inicial` (capa POO pura) en el sistema
completo NIVEC (Django + POO). Dividido en 3 sprints, 5 personas, con
contribuciones homogéneas en GitHub.

---

## Equipo

| # | Nombre | Rol |
|---|---|---|
| 1 | __________ | Líder / Integrador |
| 2 | __________ | Backend Usuarios |
| 3 | __________ | Backend Académico |
| 4 | __________ | POO / Mallas |
| 5 | __________ | Frontend / Permisos |

---

## Reglas para Contribuciones Homogéneas en GitHub

Para que las estadísticas de GitHub (Contributors) sean parejas:

1. **Cada persona hace commits desde SU computadora** (con su cuenta Git)
2. **Mínimo 3 commits por sprint** (no subir todo en 1 solo commit gigante)
3. **Cada persona crea su propio PR** en GitHub
4. **NO usar Squash Merge** — usar "Create a merge commit" para conservar commits
5. **NUNCA pushear directo a main** — siempre vía PR
6. **Formato de commits:** `feat(modulo): descripción en español`

### Meta por persona al finalizar:
- ~9-15 commits
- ~900-1100 líneas agregadas
- 3 Pull Requests (uno por sprint)

---


## Comandos Git (para todos)

```bash
# ═══ AL INICIO DE CADA SPRINT ═══
git checkout main
git pull origin main
git checkout -b sprint-X/mi-tarea

# ═══ MIENTRAS TRABAJO (mínimo 3 commits) ═══
git add .
git commit -m "feat(modulo): lo que hice"

# ═══ AL TERMINAR ═══
git push origin sprint-X/mi-tarea
# → Ir a GitHub → crear Pull Request hacia main
# → Esperar que un compañero apruebe → Merge (NO squash)

# ═══ DESPUÉS DEL MERGE ═══
git checkout main
git pull origin main
```

---

## Diagrama de Ramas

```
main
│
├─ sprint-1/estructura-proyecto      [P1] ──┐
├─ sprint-1/poo-mejoras              [P4] ──┤ merge en ORDEN
├─ sprint-1/modelos-usuarios         [P2] ──┤ (1→4→2→3→5)
├─ sprint-1/modelos-academico        [P3] ──┤
├─ sprint-1/templates-base           [P5] ──┘
│
├─ sprint-2/services-carga-masiva    [P1] ──┐
├─ sprint-2/autenticacion-paneles    [P2] ──┤ merge en
├─ sprint-2/views-entidades          [P3] ──┤ CUALQUIER orden
├─ sprint-2/views-mallas-periodos    [P4] ──┤
├─ sprint-2/views-usuarios-crud      [P5] ──┘
│
├─ sprint-3/paralelos-horarios       [P1] ──┐
├─ sprint-3/evaluaciones             [P2] ──┤ merge en
├─ sprint-3/mtn-consolidado          [P3] ──┤ CUALQUIER orden
├─ sprint-3/informes-exportacion     [P4] ──┤
├─ sprint-3/permisos-estados         [P5] ──┘
│
└─ PROYECTO COMPLETO ✓
```

---


## CRONOLOGÍA PASO A PASO

A continuación, el orden EXACTO en que se trabaja. Cada paso indica
quién lo hace, qué rama crea, y qué debe entregar.

---

### SPRINT 1 — Base del Sistema (3-4 días)

---

#### PASO 1 → Persona 1: Estructura del proyecto Django

**Rama:** `sprint-1/estructura-proyecto`
**Commits sugeridos:**
```
feat(nivec): crear settings.py con SQLite y configuración base
feat(nivec): crear urls.py, wsgi.py, manage.py
feat(proyecto): agregar .env, .gitignore, requirements.txt
```

**Archivos a crear:**
- `django/manage.py`
- `django/nivec/__init__.py`, `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`
- `django/academico/__init__.py`, `apps.py`
- `django/usuarios/__init__.py`, `apps.py`
- `django/templates/` (carpeta vacía)
- `django/static/` (carpeta vacía)
- `.env`, `.gitignore`, `requirements.txt`

**Detalle settings.py:**
- AUTH_USER_MODEL = "usuarios.UsuarioDeSistema"
- SQLite por defecto, PostgreSQL si DATABASE_URL existe
- LANGUAGE_CODE = "es", TIME_ZONE = "America/Guayaquil"
- INSTALLED_APPS: usuarios, academico

**Verificación:** `cd django && python manage.py check` pasa sin errores.
**Merge:** PRIMERO (todos dependen de esto).

---

#### PASO 2 → Persona 4: Mejoras a la capa POO

**Rama:** `sprint-1/poo-mejoras`
**Commits sugeridos:**
```
refactor(poo): mover clases/ a poo/clases/ y actualizar imports
feat(poo): agregar encapsulación y validaciones a entidades base
feat(poo): agregar franja_horaria.py y métodos para Django
```

**Qué hacer:**
1. Mover `clases/` → `poo/clases/` (agregar `poo/__init__.py`)
2. Cambiar TODOS los imports de `clases.xxx` a `poo.clases.xxx`
3. Agregar properties y métodos de validación a:
   - universidad.py, campus.py, carrera.py, unidad_curricular.py
4. Agregar `poo/clases/franja_horaria.py` (constantes de horarios)
5. Fix: `Optional[IAsignableAHorario]` en vez de `| None` (Python 3.9)

**Verificación:** `python -c "from poo.clases.universidad import Universidad; print('OK')"`
**Merge:** SEGUNDO (después de Persona 1).

---


#### PASO 3 → Persona 2: Modelos de Usuarios

**Rama:** `sprint-1/modelos-usuarios`
**Commits sugeridos:**
```
feat(usuarios): crear modelo UsuarioDeSistema (custom user)
feat(usuarios): crear PerfilDocente y PerfilEstudiante
feat(usuarios): crear PerfilAdministrativo y configurar admin
```

**Modelos:**
- CreadorDeUsuarios (BaseUserManager)
- UsuarioDeSistema (AbstractBaseUser) — USERNAME_FIELD = "correo_institucional"
- PerfilDocente — OneToOne(Usuario), vinculacion, carga horaria, jornadas
- PerfilEstudiante — OneToOne(Usuario), matrícula, jornada, carrera, cupo
- PerfilAdministrativo — OneToOne(Usuario), perfil, coordinador DAN/UA

**Nota:** FK a academico se declaran como strings: `'academico.Universidad'`
**Verificación:** `python manage.py makemigrations usuarios` genera migraciones.
**Merge:** TERCERO (después de Persona 4).

---

#### PASO 4 → Persona 3: Modelos Académicos

**Rama:** `sprint-1/modelos-academico`
**Commits sugeridos:**
```
feat(academico): crear modelos Universidad, Campus, Carrera, Malla, UC
feat(academico): crear modelos Periodo, Paralelo, Horario, Cohorte
feat(academico): crear modelos Evaluación, Incidencia, Desempeño, Informe + admin
```

**15 modelos en orden de dependencia FK:**
1. Universidad → 2. Campus → 3. Carrera → 4. MallaCurricular →
5. UnidadCurricular → 6. PeriodoDeNivelacion → 7. Paralelo →
8. Horario → 9. CohorteDeMatricula → 10. MatriculaParalelo →
11. ConsolidadoAcademico → 12. EvaluacionAcademica →
13. IncidenciaAcademica → 14. EvaluacionDeDesempeno → 15. InformeGeneral

**Helper:** `cambiar_enum_a_choices(enum_clase)` convierte enums POO a choices Django.
**Verificación:** `python manage.py makemigrations academico && python manage.py migrate`
**Merge:** CUARTO (después de Persona 2).

---

#### PASO 5 → Persona 5: Templates Base y CSS

**Rama:** `sprint-1/templates-base`
**Commits sugeridos:**
```
feat(templates): crear base.html con navbar y mensajes
feat(templates): crear base_formulario.html y base_listar.html
feat(static): crear estilos.css con diseño del sistema
```

**Archivos:**
- `django/templates/base.html` — Navbar, mensajes, block contenido
- `django/templates/base_formulario.html` — Título + formulario + botones
- `django/templates/base_listar.html` — Título + tabla + botón registrar
- `django/static/css/estilos.css` — Estilos generales

**Verificación:** `python manage.py runserver` → base.html carga sin errores.
**Merge:** QUINTO (último del Sprint 1).

---

### ✅ FIN SPRINT 1 — Todos hacen: `git checkout main && git pull origin main`

---


### SPRINT 2 — Funcionalidades CRUD (5-7 días)

**Prerequisito:** Sprint 1 mergeado. Todos parten de main actualizado.
**Merge:** En CUALQUIER orden (las 5 tareas son independientes entre sí).

---

#### PASO 6 → Persona 1: Services de Carga Masiva

**Rama:** `sprint-2/services-carga-masiva`
**Commits sugeridos:**
```
feat(utils): crear generar_identificador_siguiente y roles
feat(academico): services de carga masiva campus, carreras, mallas, unidades
feat(usuarios): services de carga masiva administrativos, docentes, estudiantes
```

**Archivos:**
- `django/usuarios/utils.py` — generar_identificador_siguiente, ROL_*, obtener_rol_usuario, requiere_perfil
- `django/academico/services.py` — normalizar_texto, obtener_enum_flexible, servicio_campus/carrera/malla/unidad_registrar_masivo
- `django/usuarios/services.py` — servicio_iniciar/cerrar_sesion, servicio_*_registrar_masivo

**Patrón:** Cada servicio retorna `{"exitosos": int, "advertencias": [], "error": str|None}`

---

#### PASO 7 → Persona 2: Autenticación y Paneles

**Rama:** `sprint-2/autenticacion-paneles`
**Commits sugeridos:**
```
feat(auth): crear vista iniciar_sesion y cerrar_sesion
feat(paneles): crear panel_principal con redirección por rol
feat(paneles): crear dashboards por rol (DAN, UA, docente, estudiante)
```

**Vistas:** iniciar_sesion, cerrar_sesion, panel_principal, panel_director_dan,
panel_dan, panel_ua, panel_docente, panel_estudiante

**Templates:** autenticacion/iniciar_sesion.html, administrativo/panel_*.html,
docente/panel_docente.html, estudiante/panel_estudiante.html

---

#### PASO 8 → Persona 3: Views Universidad, Campus, Carreras

**Rama:** `sprint-2/views-entidades`
**Commits sugeridos:**
```
feat(universidad): vista detalle, registrar, modificar
feat(campus): listar, registrar, modificar, eliminar, carga masiva Excel
feat(carrera): listar, registrar, modificar, eliminar, carga masiva Excel
```

**Forms:** FormularioUniversidad, FormularioCampus, FormularioCarrera
**Cada form usa POO para validar** (ej: `CarreraBase.esta_activa()`)

---

#### PASO 9 → Persona 4: Views Mallas, Periodos, Unidades

**Rama:** `sprint-2/views-mallas-periodos`
**Commits sugeridos:**
```
feat(malla): listar, registrar, modificar, eliminar, clonar (Prototype), cambiar estado
feat(unidad): listar, registrar, modificar, eliminar, carga masiva
feat(periodo): listar, registrar, modificar, eliminar, iniciar, finalizar
```

**Funcionalidades especiales:**
- Malla: clonar usa `MallaCurricular.clonar()` (Prototype POO)
- Periodo: iniciar/finalizar cambia estado vía `PeriodoDeNivelacion` POO

---

#### PASO 10 → Persona 5: Views CRUD de Usuarios

**Rama:** `sprint-2/views-usuarios-crud`
**Commits sugeridos:**
```
feat(docentes): listar, registrar, modificar, eliminar, inhabilitar/habilitar
feat(estudiantes): listar, registrar, modificar, eliminar, retiro, anular
feat(administrativos): listar, registrar (admin, coordinadores DAN, coordinadores UA)
```

**Forms:** FormularioUsuarioDeSistema, FormularioModificarUsuarioDeSistema,
FormularioPerfilEstudiante, FormularioRegistrarDocente, FormularioPerfilAdministrativo,
FormularioRegistrarCoordinadorDAN, FormularioRegistrarCoordinadorUA

**Nota:** Usar `@requiere_perfil(ROL_DIRECTOR_DAN, ...)` en cada vista.

---

### ✅ FIN SPRINT 2 — Todos hacen: `git checkout main && git pull origin main`

---


### SPRINT 3 — Funcionalidades Avanzadas (7-10 días)

**Prerequisito:** Sprint 2 mergeado. Todos parten de main actualizado.
**Merge:** En CUALQUIER orden (las 5 tareas son independientes entre sí).

---

#### PASO 11 → Persona 1: Paralelos y Horarios

**Rama:** `sprint-3/paralelos-horarios`
**Commits sugeridos:**
```
feat(paralelos): generar automático, listar, detalle, eliminar
feat(horarios): registrar, editar, eliminar, generar sugerido, matriz visual
feat(docente): asignar/quitar docente de paralelo
```

**Services:** servicio_generar_paralelos, servicio_mover/retirar/agregar_estudiante,
servicio_registrar/editar_horario, servicio_generar_horario_sugerido,
servicio_asignar/quitar_docente

**Usa:** Facade, DistribuidorDeEstudiantes, Paralelo POO, franja_horaria

---

#### PASO 12 → Persona 2: Evaluaciones Académicas

**Rama:** `sprint-3/evaluaciones`
**Commits sugeridos:**
```
feat(evaluacion): listar calificaciones por paralelo, detalle, editar
feat(evaluacion): carga masiva de calificaciones desde Excel
feat(evaluacion): flujo revisión (borrador → revisión → formalizado)
```

**Flujo:** Docente carga (Borrador) → Docente pasa a revisión → Coordinador formaliza
**Usa:** EvaluacionAcademica POO con Chain of Responsibility

---

#### PASO 13 → Persona 3: MTN y Consolidado

**Rama:** `sprint-3/mtn-consolidado`
**Commits sugeridos:**
```
feat(mtn): vista procesar MTN con carga Excel de estudiantes
feat(mtn): integrar DepuradorDeSincronizacion para validación
feat(consolidado): generar y mostrar estadísticas del consolidado
```

**Funcionalidades:** Subir Excel MTN → validar con CriterioCedulaFormato →
crear estudiantes → generar ConsolidadoAcademico con estadísticas

---

#### PASO 14 → Persona 4: Informes y Exportación

**Rama:** `sprint-3/informes-exportacion`
**Commits sugeridos:**
```
feat(informe): vista informe general con estadísticas por carrera
feat(informe): exportar a Excel y TXT
feat(informe): emitir informe, gestión de cohortes
```

**Services:** servicio_generar_informe_general, servicio_exportar_informe
**Usa:** ProcesadorDeInforme POO, InformeGeneral POO, Facade

---

#### PASO 15 → Persona 5: Sistema de Permisos por Estado

**Rama:** `sprint-3/permisos-estados`
**Commits sugeridos:**
```
feat(permisos): crear obtener_permisos_periodo con ~40 permisos booleanos
feat(permisos): crear context_processor para inyectar en templates
feat(templates): integrar {% if puede_X %} en todos los botones/acciones
```

**Tabla de permisos por estado:**
| Estado | Estructura | Estudiantes | Horarios | Calificaciones |
|---|---|---|---|---|
| Sin periodo | ✅ | ✅ | ❌ | ❌ |
| Planificación | ✅ | ✅ | ✅ | ❌ |
| En curso | ❌ | ✅ | ❌ | ❌ |
| Evaluación | ❌ | ❌ | ❌ | ✅ |
| Cerrado | ❌ | ❌ | ❌ | ❌ |

---

### ✅ FIN SPRINT 3 — PROYECTO COMPLETO

---


## Resumen de Contribuciones Esperadas

| Persona | Sprint 1 | Sprint 2 | Sprint 3 | Commits | Líneas |
|---|---|---|---|---|---|
| 1 | Estructura Django | Services carga masiva | Paralelos/Horarios | ~9-12 | ~1050 |
| 2 | Modelos usuarios | Auth + Paneles | Evaluaciones | ~9-12 | ~1000 |
| 3 | Modelos académicos | Views entidades | MTN + Consolidado | ~9-12 | ~950 |
| 4 | POO mejoras | Mallas/Periodos/UC | Informes | ~9-12 | ~1050 |
| 5 | Templates + CSS | CRUD usuarios | Permisos | ~9-12 | ~950 |

---

## Cómo Ejecutar (presentación offline)

```bash
git clone https://github.com/basurtovera21/estado_inicial.git
cd estado_inicial/django
pip install django openpyxl python-dotenv dj-database-url
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
# Abrir: http://127.0.0.1:8000/
```

---

## Patrones de Diseño

| Patrón | Archivo | Uso |
|---|---|---|
| Facade | centro_de_operacion_academica.py | Punto de entrada a POO |
| Prototype | malla_curricular.py → clonar() | Clonar mallas |
| Chain of Responsibility | manejadores_de_aprobacion.py | Verificar aprobación |
| Observer | i_sujeto_de_evaluacion.py | Notificar cambios |
| Strategy | i_criterio_filtro.py | Validación intercambiable |

## Principios SOLID

| Principio | Ejemplo |
|---|---|
| SRP | Cada clase = una responsabilidad |
| OCP | Nuevos manejadores sin modificar existentes |
| LSP | Manejadores intercambiables |
| ISP | IUnidadEvaluable solo 2 métodos |
| DIP | services.py usa abstracciones POO |
