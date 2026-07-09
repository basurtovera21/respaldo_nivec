# INFORME TÉCNICO — CAPA DE PROGRAMACIÓN ORIENTADA A OBJETOS (POO)
## Sistema NIVEC — Sistema Técnico de Control de Nivelación en Educación Superior

**Universidad Laica "Eloy Alfaro" de Manabí — Facultad de Ciencias de la Vida y Tecnologías**
**Carrera de Software — Asignatura: Programación Orientada a Objetos**
**Docente:** Ing. Jharol Ormaza
**Periodo académico ordinario 2026-1**

**Integrantes:**
- Basurto Vera Carlos Eduardo
- Del Mónaco Palma Luís Ángel
- Macías Mera Dengy Rodolfo
- Sánchez Peraza Anthony José
- Velasteguí Solorzano Vinicio Alejandro

**Alcance de este informe:** este documento cubre exclusivamente la carpeta `poo/` del
repositorio `respaldo_nivec`, es decir, el núcleo de dominio orientado a objetos que sostiene
al sistema NIVEC. No se documenta la capa `django/` (persistencia, vistas, formularios), salvo
como referencia de cómo consume a la capa POO.

---

# PARTE 1 — ENFOQUE DEL PROYECTO Y OBJETIVO

## 1.1 Contexto y problemática que origina NIVEC

De acuerdo con el documento de definición del proyecto, NIVEC nace para resolver un
**distanciamiento operativo** entre la normativa nacional de nivelación (Reglamento del
Sistema Nacional de Nivelación y Admisión, Acuerdo SENESCYT-SENESCYT-2024-0055-AC) y la
ejecución manual y descentralizada de dicho proceso en las Instituciones de Educación
Superior. Esto provoca:

- Dispersión de información en registros no estandarizados.
- Errores en la validación de partícipes autorizados (cotejados solo contra el consolidado
  de aceptados).
- Desajustes en la distribución de estudiantes y solapamientos horarios al no existir una
  plataforma que articule malla curricular, paralelos y carga docente.
- Falta de interoperabilidad entre el procesamiento de calificaciones (externo) y los
  registros oficiales, comprometiendo los plazos legales para el Informe General de
  Nivelación (Art. 67 de la normativa).

## 1.2 Objetivo general del sistema

Construir una **plataforma técnica unificada** que coordine cuatro frentes: (A) estructuración
y configuración de la oferta académica a partir de la Matriz de Tercer Nivel (MTN), (B)
administración de recursos y planta docente, (C) consolidación de rendimiento e
interoperabilidad con sistemas externos de calificación, y (D) generación del Informe General
de Nivelación conforme al marco legal vigente.

## 1.3 Objetivo específico de la capa POO (lo que hoy está implementado)

La carpeta `poo/` materializa el **modelo de dominio puro** del sistema: las reglas de negocio,
las validaciones normativas y los algoritmos de asignación/evaluación, **completamente
independientes de Django, de la base de datos y de la interfaz web**. Esta capa responde a la
necesidad académica de la asignatura (aplicar clases, herencia, polimorfismo, interfaces,
encapsulación, sobrecarga y patrones de diseño) y, a la vez, resuelve un problema real de
arquitectura: mantener la lógica de negocio testeable y reutilizable, de modo que Django solo
la orqueste (a través de `services.py` y `views/`) sin reimplementar las reglas.

En términos de la definición de alcance (secciones A–D del documento del proyecto), la capa
POO implementa hoy:

| Componente del alcance | Clases POO que lo implementan |
|---|---|
| A. Oferta académica (MTN, mallas, paralelos) | `Universidad`, `Campus`, `Carrera`, `MallaCurricular`, `UnidadCurricular`, `PeriodoDeNivelacion`, `Paralelo`, `DepuradorDeSincronizacion`, `DistribuidorDeEstudiantes` |
| B. Recursos y planta docente | `Docente`, `Horario`, `franja_horaria.py`, `IncidenciaAcademica`, `EvaluacionDeDesempeno`, `EstrategiaDeEvaluacionEstandar` |
| C. Consolidación de rendimiento | `EvaluacionAcademica`, `manejadores_de_aprobacion.py`, `observadores_de_evaluacion.py`, `ConsolidadoAcademico` |
| D. Informe general y cumplimiento legal | `InformeGeneral`, `MonitorNormativo`, `ProcesadorDeInforme`, `CohorteDeMatricula` |

La capa POO **no realiza I/O** (no lee Excel, no accede a la base de datos, no genera archivos
reales): esas responsabilidades quedan en `django/academico/services.py` y
`django/usuarios/services.py`, que instancian objetos POO, invocan sus métodos de validación
y comportamiento, y persisten el resultado en los modelos Django. Esta separación es la
aplicación central del principio de **Responsabilidad Única (SRP)** a nivel de arquitectura.

---

# PARTE 2 — ARQUITECTURA DE LA CAPA POO

## 2.1 Estructura de directorios

```
poo/
└── clases/
    ├── campus.py                     # Entidad
    ├── carrera.py                    # Entidad
    ├── cohorte_de_matricula.py       # Entidad
    ├── consolidado_academico.py      # Entidad
    ├── evaluacion_academica.py       # Entidad + Observer (Sujeto) + Chain of Responsibility
    ├── evaluacion_de_desempeno.py    # Entidad + Strategy (contexto)
    ├── franja_horaria.py             # Módulo de reglas normativas (funciones puras)
    ├── horario.py                    # Entidad de valor
    ├── incidencia_academica.py       # Entidad
    ├── informe_general.py            # Entidad + implementa IInformeInstitucional
    ├── malla_curricular.py           # Entidad + Prototype (IClonable)
    ├── paralelo.py                   # Entidad (agregado de horarios/estudiantes)
    ├── periodo_de_nivelacion.py      # Entidad (máquina de estados)
    ├── unidad_curricular.py          # Entidad + implementa IUnidadEvaluable
    ├── universidad.py                # Entidad
    │
    ├── criterios_filtro/             # Strategy de validación
    │   ├── criterio_cedula_formato.py
    │   └── criterio_consistente_de_horas.py
    │
    ├── enums/                        # 21 enumeraciones de dominio
    │   ├── dia_de_semana.py, jornada.py, modalidad.py, ...
    │
    ├── interfaces/                   # Contratos abstractos (ABC)
    │   ├── i_asignable_a_horario.py
    │   ├── i_clonable.py
    │   ├── i_criterio_filtro.py
    │   ├── i_estrategia_de_evaluacion.py
    │   ├── i_informe_institucional.py
    │   ├── i_manejador_de_aprobacion.py
    │   ├── i_observador_de_evaluacion.py
    │   ├── i_sujeto_de_evaluacion.py
    │   └── i_unidad_evaluable.py
    │
    ├── servicios/                    # Orquestadores de dominio (Facade, Strategy, etc.)
    │   ├── centro_de_operacion_academica.py   # Facade
    │   ├── depurador_de_sincronizacion.py     # Usa Strategy (ICriterioFiltro)
    │   ├── distribuidor_de_estudiantes.py     # Algoritmo de balanceo
    │   ├── estrategia_de_evaluacion_estandar.py
    │   ├── manejadores_de_aprobacion.py       # Chain of Responsibility (concreto)
    │   ├── monitor_normativo.py               # Alertas de vencimiento
    │   ├── observadores_de_evaluacion.py      # Observer (concreto)
    │   └── procesador_de_informe.py           # Exportación
    │
    └── usuarios/                     # Jerarquía de herencia
        ├── usuario_de_sistema.py     # Clase abstracta raíz
        ├── usuario_academico.py      # Intermedia (Docente/Estudiante)
        ├── usuario_administrativo.py # Intermedia (CoordinadorDAN/UA)
        ├── docente.py
        ├── estudiante.py
        ├── coordinador_dan.py
        └── coordinador_unidad_academica.py
```

**Nota de implementación:** el paquete no usa archivos `__init__.py` (se apoya en el soporte de
*namespace packages* de Python 3). Se verificó su importabilidad ejecutando
`from poo.clases.universidad import Universidad`, la cual se resuelve correctamente. Es la
misma forma en que la capa Django la consume (20 archivos de `django/academico/` y
`django/usuarios/` hacen `from poo.clases...` según se confirmó con una búsqueda en el código).

## 2.2 Métricas generales de la capa

- **63 archivos `.py`**
- **≈ 3.900 líneas de código**
- **21 enumeraciones** (`enums/`)
- **9 interfaces abstractas** (`interfaces/`)
- **8 servicios de dominio** (`servicios/`)
- **7 clases de la jerarquía de usuarios**
- **15 entidades de dominio académico** (`Universidad`, `Campus`, `Carrera`,
  `MallaCurricular`, `UnidadCurricular`, `PeriodoDeNivelacion`, `Paralelo`, `Horario`,
  `CohorteDeMatricula`, `ConsolidadoAcademico`, `EvaluacionAcademica`,
  `EvaluacionDeDesempeno`, `IncidenciaAcademica`, `InformeGeneral`, y el módulo funcional
  `franja_horaria`)

## 2.3 Principios SOLID aplicados (evidencia concreta en el código)

| Principio | Evidencia en la capa POO |
|---|---|
| **S**RP | Cada clase resuelve una sola responsabilidad: `Campus` solo valida datos de un campus; `DistribuidorDeEstudiantes` solo distribuye; `MonitorNormativo` solo evalúa vencimientos. |
| **O**CP | Nuevas reglas de aprobación se agregan creando un nuevo `IManejadorDeAprobacion` sin tocar `EvaluacionAcademica`. Nuevas estrategias de evaluación docente se agregan implementando `IEstrategiaDeEvaluacion`. |
| **L**SP | `ManejadorEstadoInactivo`, `ManejadorAsistencia` y `ManejadorCalificacion` son intercambiables entre sí porque comparten el contrato `manejar()`. Toda subclase de `UsuarioDeSistema` puede sustituirse donde se espera la clase base (todas implementan `iniciar_sesion()`). |
| **I**SP | `IUnidadEvaluable` solo exige 2 métodos (`obtener_codigo_de_unidad`, `obtener_horas_totales`); `IAsignableAHorario` solo exige `nombres` y `apellidos`; ninguna interfaz obliga a implementar métodos que la clase no necesita. |
| **D**IP | `DepuradorDeSincronizacion` depende de la abstracción `ICriterioFiltro`, no de `CriterioCedulaFormato` en concreto; `CentroDeOperacionAcademica` (Facade) coordina objetos de dominio sin acoplarse a Django. |

## 2.4 Patrones de diseño identificados en el código

| Patrón | Tipo | Ubicación | Rol |
|---|---|---|---|
| **Facade** | Estructural | `servicios/centro_de_operacion_academica.py` | Punto único de entrada para que Django opere sobre 7 subsistemas POO (estudiantes, docentes, distribución, evaluación, periodos, cohortes, informes). |
| **Prototype** | Creacional | `malla_curricular.py` (`IClonable`) | `MallaCurricular.clonar()` usa `copy.deepcopy` para generar nuevas versiones de malla sin reconstruir unidad por unidad. |
| **Chain of Responsibility** | Comportamiento | `interfaces/i_manejador_de_aprobacion.py` + `servicios/manejadores_de_aprobacion.py` | Verifica la aprobación académica en cadena: estado inactivo → asistencia → calificación. |
| **Observer** | Comportamiento | `interfaces/i_sujeto_de_evaluacion.py`, `i_observador_de_evaluacion.py` + `servicios/observadores_de_evaluacion.py` | `EvaluacionAcademica` notifica a observadores cuando cambia el estado de aprobación. |
| **Strategy** | Comportamiento | `interfaces/i_criterio_filtro.py`, `i_estrategia_de_evaluacion.py` + `criterios_filtro/`, `servicios/estrategia_de_evaluacion_estandar.py` | Algoritmos de validación (cédula, consistencia de horas) y de ponderación de desempeño docente, intercambiables sin tocar el consumidor. |

Adicionalmente, `abc.ABCMeta`/`abstractmethod` se usa de forma consistente en toda la capa
(`UsuarioDeSistema`, las 9 interfaces) para forzar contratos, y se aplican **sobrecarga de
métodos** mediante `*args` (ver `EvaluacionAcademica.registrar_calificacion` y
`MallaCurricular.agregar_unidad_curricular`) — un mecanismo típico en Python para simular la
sobrecarga que en otros lenguajes (Java, C#) es nativa.

*(Continúa en la Parte 3.)*



---

# PARTE 3 — DESARROLLO: PASOS SEGUIDOS Y CÓDIGO FUENTE COMENTADO

Esta parte reconstruye el desarrollo de la capa POO organizándolo por **bloques de
responsabilidad**, en el orden lógico en que un objeto de dominio depende de otro
(enumeraciones → interfaces → entidades base → jerarquía de usuarios → entidades
compuestas → servicios/patrones → integración con Django). Este es también, en la práctica,
el orden en que el equipo debió construirlas: primero el "vocabulario" (enums), luego los
"contratos" (interfaces), y solo después las clases concretas que dependen de ambos.

## 3.1 Paso 1 — Vocabulario del dominio: las enumeraciones (`enums/`)

Antes de escribir cualquier entidad, el equipo definió **21 enumeraciones** (`Enum` de Python)
que representan los valores cerrados del dominio de nivelación: estados de matrícula, de
periodo, de vinculación docente, jornadas, modalidades, etc. Usar `Enum` en vez de cadenas de
texto sueltas evita errores de escritura y centraliza los valores permitidos.

```python
# poo/clases/enums/estado_de_periodo.py
from enum import Enum

class EstadoDePeriodo(Enum):
    PLANIFICACION = "Planificación"
    EN_CURSO = "En curso"
    EVALUACION = "Evaluación"
    CERRADO = "Cerrado"
```

```python
# poo/clases/enums/estado_de_aprobacion.py
from enum import Enum

class EstadoDeAprobacion(Enum):
    PENDIENTE = "Pendiente"
    APROBADO = "Aprobado"
    REPROBADO = "Reprobado"
    RETIRADO = "Retirado"
    ANULADO = "Anulado"
```

Estas dos enumeraciones son las que gobiernan las dos "máquinas de estado" más importantes
del sistema: el ciclo de vida del **periodo de nivelación** y el resultado final de una
**evaluación académica**. El resto de enumeraciones (`Jornada`, `Modalidad`,
`TipoDeIdentificacion`, `EstadoDeVinculacion`, `PerfilAdministrativo`, `RegistroDeCupo`,
`TipoDeCohorte`, `EstadoDeCohorte`, `EstadoDeMalla`, `EstadoDeUsuario`,
`EstadoDeInforme`, `TipoDeInforme`, `EstadoDeAlerta`, `FormatoDeExportacion`,
`TiempoDeDedicacion`, `TipoDeVinculacion`, `TipoDeComponente`, `TipoDeSesion`,
`DiaDeSemana`) siguen el mismo patrón: una clase pequeña, inmutable, sin lógica.

Nota técnica registrada en `PLAN_DE_TRABAJO.md`: en las clases que reciben una enumeración
como parámetro opcional se usa `Optional[Tipo]` (de `typing`) en lugar del operador `Tipo |
None`, porque el proyecto declara compatibilidad con Python 3.9, donde la sintaxis con `|`
para *type hints* todavía no estaba disponible (se introdujo en 3.10). Esto se ve, por ejemplo,
en `horario.py`:

```python
# poo/clases/horario.py (fragmento)
from typing import Optional
from poo.clases.interfaces.i_asignable_a_horario import IAsignableAHorario

class Horario:
    def __init__(self, dia_semana: DiaDeSemana, hora_inicio: time, hora_fin: time,
                 espacio_de_imparticion: str = "",
                 docente_responsable: Optional[IAsignableAHorario] = None, **kwargs):
        ...
```

## 3.2 Paso 2 — Los contratos: interfaces abstractas (`interfaces/`)

Con el vocabulario definido, el equipo declaró **9 interfaces** usando `abc.ABCMeta` y
`@abstractmethod`. En Python no existe la palabra reservada `interface` como en Java, por lo
que el patrón estándar es crear una clase base abstracta que solo declara métodos sin
implementación. Estas interfaces son la base de todos los patrones de diseño de la capa.

```python
# poo/clases/interfaces/i_criterio_filtro.py
from abc import ABCMeta, abstractmethod

class ICriterioFiltro(metaclass=ABCMeta):
    """
    Contrato Strategy: cada criterio de validación evalúa un aspecto puntual
    de un registro (dict) y decide si es válido, sin que el consumidor
    (DepuradorDeSincronizacion) conozca los detalles de la validación.
    """
    @abstractmethod
    def es_valido(self, registro: dict) -> bool:
        pass
```

```python
# poo/clases/interfaces/i_manejador_de_aprobacion.py (fragmento)
from abc import ABCMeta, abstractmethod

class IManejadorDeAprobacion(metaclass=ABCMeta):
    def __init__(self, siguiente=None):
        self._siguiente = siguiente          # Referencia al siguiente eslabón

    @property
    def siguiente(self):
        return self._siguiente

    @abstractmethod
    def manejar(self, evaluacion):
        """Procesa la evaluación o la delega al siguiente manejador."""
        pass
```

Cada interfaz respeta el **Principio de Segregación de Interfaces (ISP)**: por ejemplo,
`IUnidadEvaluable` solo exige dos métodos porque es lo único que `MallaCurricular` necesita
de una unidad curricular para calcular horas totales; no se le exige exponer criterios de
aprobación, asistencia, etc.

```python
# poo/clases/interfaces/i_unidad_evaluable.py
from abc import ABCMeta, abstractmethod

class IUnidadEvaluable(metaclass=ABCMeta):
    @abstractmethod
    def obtener_codigo_de_unidad(self):
        pass

    @abstractmethod
    def obtener_horas_totales(self):
        pass
```

## 3.3 Paso 3 — Entidades básicas de infraestructura académica

Con el vocabulario y los contratos listos, se construyeron las entidades "hoja" que no
dependen de otras clases del dominio: `Universidad`, `Campus`, `Carrera`. Todas comparten el
mismo estilo: **atributos privados** (`self._atributo`) expuestos mediante `@property`,
validación de datos separada del constructor (`validar_datos_de_registro()`), y detección de
duplicados por normalización de texto (quitando tildes y mayúsculas) para comparaciones
robustas frente a errores de tipeo en cargas masivas desde Excel.

```python
# poo/clases/universidad.py (fragmento clave)
class Universidad:
    _LONGITUD_MAXIMA_ABREVIATURA = 20

    def __init__(self, nombre: str, abreviatura: str, codigo_sniese: str, direccion_matriz: str = ""):
        self._nombre = nombre
        self._abreviatura = abreviatura
        self._codigo_sniese = codigo_sniese      # Encapsulado: sin setter -> es inmutable
        self._direccion_matriz = direccion_matriz

    @property
    def codigo_sniese(self):
        return self._codigo_sniese               # Solo lectura: el código SNIESE no cambia

    def validar_datos_de_registro(self) -> dict:
        """Devuelve un diccionario de errores por campo (vacío si es válido)."""
        errores = {}
        if not self._nombre or not str(self._nombre).strip():
            errores["nombre"] = "Información requerida"
        if not self._abreviatura or not str(self._abreviatura).strip():
            errores["abreviatura"] = "Información requerida"
        elif len(str(self._abreviatura).strip()) > self._LONGITUD_MAXIMA_ABREVIATURA:
            errores["abreviatura"] = f"La abreviatura no debe exceder {self._LONGITUD_MAXIMA_ABREVIATURA} caracteres"
        if not self._codigo_sniese or not str(self._codigo_sniese).strip():
            errores["codigo_sniese"] = "Información requerida"
        return errores

    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """Quita tildes/mayúsculas para comparar 'Uleam' == 'ULEAM' == 'úleam'."""
        import unicodedata
        if not texto:
            return ""
        texto = str(texto).strip().lower()
        return ''.join(c for c in unicodedata.normalize('NFD', texto)
                       if unicodedata.category(c) != 'Mn')
```

`Carrera` añade una regla temporal (vigencia SNIESE):

```python
# poo/clases/carrera.py (fragmento clave)
from datetime import date

class Carrera:
    def __init__(self, codigo_de_carrera: str, nombre: str, vigencia_sniese: date = None):
        self._codigo_de_carrera = codigo_de_carrera
        self._nombre = nombre
        self._vigencia_sniese = vigencia_sniese

    def esta_activa(self) -> bool:
        """Una carrera está vigente si hoy no ha superado su fecha SNIESE."""
        if not self._vigencia_sniese:
            return False
        return date.today() <= self._vigencia_sniese

    def calcular_dias_restantes_vigencia(self) -> int:
        if not self._vigencia_sniese:
            return 0
        return (self._vigencia_sniese - date.today()).days
```

## 3.4 Paso 4 — Jerarquía de usuarios (herencia, polimorfismo, encapsulación)

Esta es la sección donde más se concentran los pilares clásicos de la POO: **herencia
multinivel**, **herencia múltiple** (mixin de interfaz), **polimorfismo** de
`iniciar_sesion()`, y **encapsulación fuerte** de la contraseña.

```
UsuarioDeSistema (ABC)                        ← raíz abstracta, no instanciable
 ├── UsuarioAcademico                          ← intermedia (agrega identificador_institucional)
 │    ├── Docente  (+ IAsignableAHorario)      ← herencia múltiple
 │    └── Estudiante
 └── UsuarioAdministrativo                     ← intermedia (agrega perfil_administrativo)
      ├── CoordinadorDAN
      └── CoordinadorUnidadAcademica
```

```python
# poo/clases/usuarios/usuario_de_sistema.py (fragmento clave)
from abc import ABCMeta, abstractmethod
from poo.clases.enums.estado_de_usuario import EstadoDeUsuario

class UsuarioDeSistema(metaclass=ABCMeta):
    _MINIMO_CARACTERES_CONTRASENA = 8
    _MAXIMO_CARACTERES_CONTRASENA = 16

    def __init__(self, tipo_de_identificacion, identificacion, nombres, apellidos,
                 correo_institucional, contrasena, fecha_de_nacimiento, sexo, etnia,
                 porcentaje_de_discapacidad, celular, direccion, **kwargs):
        ...
        self.contrasena = contrasena          # Dispara el setter -> valida antes de guardar
        self._estado_de_usuario = EstadoDeUsuario.PENDIENTE

    @property
    def contrasena(self):
        return self.__contrasena              # Doble guion bajo -> name mangling (más privado)

    @contrasena.setter
    def contrasena(self, nueva_contrasena):
        UsuarioDeSistema.validar_contrasena(nueva_contrasena)  # Lanza ValueError si es inválida
        self.__contrasena = nueva_contrasena

    @abstractmethod
    def iniciar_sesion(self):
        """Cada subclase decide sus propias reglas de acceso (polimorfismo)."""
        pass

    @staticmethod
    def validar_contrasena(nueva_contrasena, confirmar_contrasena=None):
        if confirmar_contrasena is not None and nueva_contrasena != confirmar_contrasena:
            raise ValueError("Las contraseñas registradas no coinciden")
        if len(nueva_contrasena) < UsuarioDeSistema._MINIMO_CARACTERES_CONTRASENA:
            raise ValueError(f"La contraseña debe contener un mínimo de "
                              f"{UsuarioDeSistema._MINIMO_CARACTERES_CONTRASENA} caracteres")
        if len(nueva_contrasena) > UsuarioDeSistema._MAXIMO_CARACTERES_CONTRASENA:
            raise ValueError(f"La contraseña debe contener un máximo de "
                              f"{UsuarioDeSistema._MAXIMO_CARACTERES_CONTRASENA} caracteres")
        return True
```

El **polimorfismo** se aprecia comparando cómo cada subclase implementa `iniciar_sesion()`:

```python
# poo/clases/usuarios/docente.py (fragmento)
def iniciar_sesion(self):
    if self._estado_de_vinculacion.value == "Inactivo":
        return False              # Un docente inactivo no puede ingresar
    return True
```

```python
# poo/clases/usuarios/estudiante.py (fragmento)
def iniciar_sesion(self):
    if self._estado_de_matricula in (EstadoDeMatricula.RETIRADO, EstadoDeMatricula.ANULADO):
        return False              # Un estudiante retirado/anulado no puede ingresar
    return True
```

```python
# poo/clases/usuarios/usuario_administrativo.py (fragmento)
def iniciar_sesion(self):
    return True                   # El personal administrativo no tiene esta restricción
```

Cualquier código cliente puede invocar `usuario.iniciar_sesion()` sin conocer de qué subclase
se trata: cada objeto responde según su propia regla (polimorfismo en tiempo de ejecución).

`Docente` es el caso de **herencia múltiple**: extiende `UsuarioAcademico` (herencia de
clase) e implementa `IAsignableAHorario` (herencia de interfaz), porque un docente es, a la
vez, un usuario académico y una entidad que puede ser responsable de un bloque horario.

```python
# poo/clases/usuarios/docente.py (encabezado + método de negocio)
class Docente(UsuarioAcademico, IAsignableAHorario):
    ...
    def validar_asignacion_a_paralelo(self, paralelo, horas_de_la_unidad):
        """
        Verifica en un solo método las 3 condiciones normativas para asignar
        un docente a un paralelo: estar activo, no tener conflicto horario
        y no exceder su carga máxima permitida.
        """
        if not self.esta_activo():
            return {"ok": False, "motivo": "inactivo"}

        for horario in paralelo.horarios:
            if not self.verificar_disponibilidad_horaria(horario):
                return {"ok": False, "motivo": "conflicto", "horario_en_conflicto": horario}

        horas_nuevas = round(float(horas_de_la_unidad or 0), 2)
        if self._carga_horaria_actual + horas_nuevas > self.carga_horaria_maxima:
            return {"ok": False, "motivo": "carga",
                    "carga_actual": self._carga_horaria_actual,
                    "horas_nuevas": horas_nuevas,
                    "carga_maxima": self.carga_horaria_maxima}

        return {"ok": True, "motivo": ""}
```

`UsuarioAdministrativo` introduce una regla de negocio interesante: ciertos perfiles (el
Director DAN) no pueden ser modificados ni eliminados desde la interfaz administrativa, lo
cual se modela como comportamiento de la propia entidad, no como una condición dispersa en
las vistas de Django:

```python
# poo/clases/usuarios/usuario_administrativo.py (fragmento)
class UsuarioAdministrativo(UsuarioDeSistema):
    _PERFILES_NO_MODIFICABLES = (PerfilAdministrativo.DIRECTOR_DAN,)
    ...
    def puede_ser_modificado_o_eliminado(self) -> bool:
        return self._perfil_administrativo not in self._PERFILES_NO_MODIFICABLES
```

`CoordinadorDAN` y `CoordinadorUnidadAcademica` heredan de `UsuarioAdministrativo` y fijan su
propio `perfil_administrativo` en la llamada a `super().__init__()`, evitando que el llamador
tenga que especificarlo:

```python
# poo/clases/usuarios/coordinador_dan.py (fragmento)
class CoordinadorDAN(UsuarioAdministrativo):
    def __init__(self, ..., identificador_coordinador_dan: str, universidad=None, **kwargs):
        super().__init__(
            ...,
            perfil_administrativo=PerfilAdministrativo.COORDINADOR_DAN,  # Fijo por diseño
            universidad=universidad,
            **kwargs
        )
        self._identificador_coordinador_dan = identificador_coordinador_dan

    def puede_ser_modificado_o_eliminado(self) -> bool:
        return True   # Sobreescribe la regla del padre: este perfil sí puede modificarse
```

## 3.5 Paso 5 — Entidades académicas compuestas (dependen de las anteriores)

### `UnidadCurricular` — Strategy delegado para validar horas

```python
# poo/clases/unidad_curricular.py (fragmento clave)
class UnidadCurricular(IUnidadEvaluable):
    MINIMO_HORAS_SINCRONICAS = 6

    def validar_distribucion_de_horas_totales(self) -> bool:
        """
        No calcula la validación aquí mismo: delega a CriterioConsistenteDeHoras
        (Strategy) para que la regla "sincronicas + asincronicas == totales"
        pueda reutilizarse también en la validación de cargas masivas del
        Depurador, sin duplicar la fórmula en dos lugares.
        """
        from poo.clases.criterios_filtro.criterio_consistente_de_horas import CriterioConsistenteDeHoras
        criterio = CriterioConsistenteDeHoras()
        return criterio.es_valido({
            "horas_totales": self._horas_totales,
            "horas_sincronicas": self._horas_sincronicas,
            "horas_asincronicas": self._horas_asincronicas,
        })

    def calcular_horas_sincronicas_semanales(self, semanas: int) -> int:
        """ceil(horas_sincronicas / semanas): cuántas horas por semana exige la unidad."""
        import math
        if not semanas or semanas <= 0:
            return round(self.horas_sincronicas, 2)
        return math.ceil(self.horas_sincronicas / semanas)
```

### `MallaCurricular` — máquina de estados + Prototype + sobrecarga

```python
# poo/clases/malla_curricular.py (fragmento clave)
class MallaCurricular(IClonable):
    def __init__(self, codigo_de_malla, nombre, version_de_malla):
        self._estado = EstadoDeMalla.DISENO          # Toda malla nace en DISEÑO
        self._unidades_curriculares = []

    def activar(self) -> bool:
        """Transición válida: DISEÑO/INACTIVA -> ACTIVA."""
        if self._estado in (EstadoDeMalla.DISENO, EstadoDeMalla.INACTIVA):
            self._estado = EstadoDeMalla.ACTIVA
            return True
        return False                                  # Transición no permitida -> no cambia nada

    def clonar(self, nuevo_codigo_de_malla: str, nueva_version_de_malla: str) -> 'MallaCurricular':
        """
        Patrón Prototype: copia profunda de la malla (incluye TODAS sus unidades
        curriculares) para generar una nueva versión sin reconstruirla manualmente.
        La copia siempre nace en DISEÑO, sin importar el estado del original.
        """
        import copy
        clon = copy.deepcopy(self)
        clon._codigo_de_malla = nuevo_codigo_de_malla
        clon._version_de_malla = nueva_version_de_malla
        clon._estado = EstadoDeMalla.DISENO
        clon._total_horas_nivelacion = clon.calcular_total_horas_nivelacion()
        return clon

    def agregar_unidad_curricular(self, *args) -> bool:
        """
        Sobrecarga simulada con *args: acepta una sola unidad, una lista de
        unidades o múltiples unidades como argumentos separados.
        """
        unidad_agregada = True
        for entrada in args:
            if isinstance(entrada, list):
                for unidad in entrada:
                    if not self._agregar_una_unidad_curricular(unidad):
                        unidad_agregada = False
            else:
                if not self._agregar_una_unidad_curricular(entrada):
                    unidad_agregada = False
        return unidad_agregada
```

### `PeriodoDeNivelacion` — la máquina de estados central del sistema

```python
# poo/clases/periodo_de_nivelacion.py (fragmento clave)
class PeriodoDeNivelacion:
    def iniciar_periodo_de_nivelacion(self) -> bool:
        if self._estado == EstadoDePeriodo.PLANIFICACION and date.today() >= self._fecha_inicio:
            self._estado = EstadoDePeriodo.EN_CURSO
            return True
        return False

    def finalizar_periodo_de_nivelacion(self) -> bool:
        if self._estado in (EstadoDePeriodo.EN_CURSO, EstadoDePeriodo.EVALUACION):
            self._estado = EstadoDePeriodo.CERRADO
            return True
        return False

    def permite_configurar_horarios(self) -> bool:
        """Los horarios solo se editan durante PLANIFICACIÓN (regla usada por permisos.py en Django)."""
        return self._estado == EstadoDePeriodo.PLANIFICACION
```

Estos métodos `permite_*()` son el fundamento POO de la "Tabla de permisos por estado" descrita
en `PLAN_DE_TRABAJO.md` (Sprint 3, Persona 5): Django construye ~40 permisos booleanos para la
interfaz consultando directamente estas reglas, en lugar de reimplementarlas.

### `Paralelo` — agregado de horarios y estudiantes, con validación cruzada

```python
# poo/clases/paralelo.py (fragmento clave)
class Paralelo:
    CAPACIDAD_MINIMA = 20
    CAPACIDAD_MAXIMA_PERMITIDA = 50
    CAPACIDAD_MAXIMA_PREDETERMINADA = 35

    def validar_nuevo_horario(self, nuevo_horario, horas_sincronicas_requeridas,
                               horarios_externos=None) -> dict:
        """
        Antes de aceptar un nuevo horario en el paralelo valida dos cosas:
        1) que no choque con ningún horario existente (propio o externo,
           por ejemplo del mismo docente en otro paralelo)
        2) que la suma de horas agendadas no supere las horas sincrónicas
           que exige la unidad curricular.
        """
        conflicto = self.encontrar_conflicto_horario(nuevo_horario, horarios_externos)
        if conflicto is not None:
            return {"ok": False, "motivo": "conflicto", "horario_en_conflicto": conflicto}

        horas_actuales = self.calcular_horas_agendadas()
        horas_nuevas = nuevo_horario.determinar_duracion_horas()
        if horas_actuales + horas_nuevas > horas_sincronicas_requeridas:
            return {"ok": False, "motivo": "horas",
                    "horas_actuales": horas_actuales, "horas_nuevas": horas_nuevas}

        return {"ok": True, "motivo": ""}

    @staticmethod
    def generar_nombre_por_indice(indice: int) -> str:
        """0->'Paralelo A' ... 25->'Paralelo Z', 26->'Paralelo A1', etc."""
        letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if indice < 26:
            return f"Paralelo {letras[indice]}"
        ciclo = (indice - 26) // 26 + 1
        pos = (indice - 26) % 26
        return f"Paralelo {letras[pos]}{ciclo}"
```

### `franja_horaria.py` — módulo de reglas normativas (no es una clase)

Este archivo es deliberadamente un **módulo de funciones puras**, no una clase, porque
representa configuración estática de la normativa (franjas por jornada, límite de 20 horas
sincrónicas semanales por malla) y no una entidad con estado propio. El equipo documentó
explícitamente esta decisión de diseño en el docstring del archivo, justificándola con SRP.

```python
# poo/clases/franja_horaria.py (fragmento clave)
FRANJAS = {
    Jornada.MATUTINA: (time(7, 0), time(13, 0)),
    Jornada.VESPERTINA: (time(13, 0), time(19, 0)),
    Jornada.NOCTURNA: (time(19, 0), time(23, 0)),
}
LIMITE_HORAS_SINCRONICAS_SEMANALES_MALLA = 20   # Basado en la jornada más restrictiva (nocturna)

def validar_malla_cabe_en_horario(total_horas_sincronicas: float, semanas: int) -> dict:
    """
    Verifica que el total de horas sincrónicas de TODA la malla pueda
    distribuirse sin exceder 20h/semana, dado un número de semanas del periodo.
    """
    if semanas <= 0:
        semanas = SEMANAS_REFERENCIA_MINIMA
    horas_semanales = math.ceil(total_horas_sincronicas / semanas)
    limite = LIMITE_HORAS_SINCRONICAS_SEMANALES_MALLA
    if horas_semanales <= limite:
        return {"ok": True, "horas_semanales": horas_semanales, "limite": limite}
    return {"ok": False, "motivo": (f"La malla requiere {horas_semanales}h sincrónicas "
            f"semanales y el máximo permitido es {limite}h (con {semanas} semanas)"),
            "horas_semanales": horas_semanales, "limite": limite}
```

### `CohorteDeMatricula` y `ConsolidadoAcademico` — trazabilidad de matrícula (MTN)

```python
# poo/clases/cohorte_de_matricula.py (fragmento clave)
class CohorteDeMatricula:
    def registrar_estudiante_matriculado(self, estudiante: Estudiante):
        if self._estado_de_cohorte != EstadoDeCohorte.ABIERTA:
            return False
        if date.today() > self.fecha_de_cierre:
            return False
        if estudiante in self._estudiantes_matriculados:
            return False
        self._estudiantes_matriculados.append(estudiante)
        self._actualizar_contador_de_registro(estudiante.registro_de_cupo)
        return True

    def _actualizar_contador_de_registro(self, registro_de_cupo):
        """Clasifica automáticamente al estudiante según su tipo de cupo
        (primera matrícula, segunda matrícula o exoneración), tal como
        exige el punto 2 de 'Detalle de funcionalidades' del proyecto."""
        valor = registro_de_cupo.value if isinstance(registro_de_cupo, RegistroDeCupo) else registro_de_cupo
        if valor == RegistroDeCupo.REGULAR.value:
            self._total_primera_matricula += 1
        elif valor == RegistroDeCupo.SEGUNDA_MATRICULA.value:
            self._total_segunda_matricula += 1
        elif valor == RegistroDeCupo.EXONERACION.value:
            self._total_exonerados += 1
```

```python
# poo/clases/consolidado_academico.py (fragmento clave)
class ConsolidadoAcademico:
    def obtener_estadisticas_de_consolidado(self) -> dict:
        """Calcula el % de registros válidos frente a los cupos aceptados
        esperados, insumo directo para el Informe General de Nivelación."""
        if self.total_de_cupos_aceptados > 0:
            porcentaje_valido = (self._registros_validos / self.total_de_cupos_aceptados) * 100
            registros_validos = f"{porcentaje_valido:.2f}%"
        else:
            registros_validos = "0%"
        return {"Fecha de corte": str(self.fecha_de_corte), ...}
```

## 3.6 Paso 6 — Patrones de comportamiento aplicados a la evaluación académica

Esta es la parte más elaborada de la capa POO desde el punto de vista de patrones de diseño,
porque combina **tres patrones simultáneos** sobre una sola entidad: `EvaluacionAcademica`.

**Chain of Responsibility** — la decisión de aprobar/reprobar a un estudiante no se resuelve
con una sola función con muchos `if`, sino con una cadena de manejadores, cada uno responsable
de una sola regla normativa, en orden de prioridad legal:

```python
# poo/clases/servicios/manejadores_de_aprobacion.py (los 3 eslabones)
class ManejadorEstadoInactivo(IManejadorDeAprobacion):
    """1er eslabón: un RETIRADO/ANULADO no se evalúa más, la cadena se detiene aquí."""
    def manejar(self, evaluacion_academica):
        if evaluacion_academica._estado_de_aprobacion in (
            EstadoDeAprobacion.RETIRADO, EstadoDeAprobacion.ANULADO
        ):
            return evaluacion_academica._estado_de_aprobacion
        if self.siguiente:
            return self.siguiente.manejar(evaluacion_academica)
        return evaluacion_academica._estado_de_aprobacion


class ManejadorAsistencia(IManejadorDeAprobacion):
    """2do eslabón: asistencia insuficiente reprueba sin importar la nota."""
    def manejar(self, evaluacion_academica):
        porcentaje_minimo = evaluacion_academica.unidad_curricular.porcentaje_minimo_asistencia
        if evaluacion_academica._porcentaje_asistencia < porcentaje_minimo:
            evaluacion_academica._estado_de_aprobacion = EstadoDeAprobacion.REPROBADO
            evaluacion_academica._observacion = "Reprobado por porcentaje de asistencia insuficiente"
            return evaluacion_academica._estado_de_aprobacion
        if self.siguiente:
            return self.siguiente.manejar(evaluacion_academica)
        return evaluacion_academica._estado_de_aprobacion


class ManejadorCalificacion(IManejadorDeAprobacion):
    """3er eslabón: solo se llega aquí si el estudiante está activo y asistió lo suficiente."""
    def manejar(self, evaluacion_academica):
        criterio = evaluacion_academica.unidad_curricular.criterio_de_aprobacion
        if evaluacion_academica._nota_final >= criterio:
            evaluacion_academica._estado_de_aprobacion = EstadoDeAprobacion.APROBADO
            evaluacion_academica._observacion = "Aprobado"
        else:
            evaluacion_academica._estado_de_aprobacion = EstadoDeAprobacion.REPROBADO
            evaluacion_academica._observacion = "Reprobado por calificación insuficiente"
        if self.siguiente:
            return self.siguiente.manejar(evaluacion_academica)
        return evaluacion_academica._estado_de_aprobacion
```

**Observer** — cuando la cadena anterior cambia el estado, `EvaluacionAcademica` (que hereda
de `ISujetoDeEvaluacion`) notifica automáticamente a quien esté suscrito:

```python
# poo/clases/evaluacion_academica.py (fragmento clave)
class EvaluacionAcademica(ISujetoDeEvaluacion):
    def __init__(self, estudiante, unidad_curricular):
        super().__init__()   # Inicializa self._observadores = [] (lado Sujeto del Observer)
        ...
        # La cadena se ensambla una sola vez en el constructor:
        self._cadena_aprobacion = ManejadorEstadoInactivo(
            ManejadorAsistencia(ManejadorCalificacion())
        )

    def registrar_calificacion(self, *args):
        """
        Sobrecarga: registrar_calificacion(1, 8.5) fija solo el parcial 1;
        registrar_calificacion(8.5, 9.0) fija ambos parciales a la vez.
        """
        if self._estado_de_aprobacion != EstadoDeAprobacion.PENDIENTE:
            return False   # Ya no se puede modificar una evaluación finalizada
        if len(args) == 2 and isinstance(args[0], int):
            parcial, nota = args
            return self._definir_en_parcial(parcial, nota)
        elif len(args) == 2 and isinstance(args[0], float):
            r1 = self._definir_en_parcial(1, args[0])
            r2 = self._definir_en_parcial(2, args[1])
            return r1 and r2
        return False

    def verificar_aprobacion(self) -> EstadoDeAprobacion:
        estado_anterior = self._estado_de_aprobacion
        self._cadena_aprobacion.manejar(self)          # Dispara Chain of Responsibility
        if (estado_anterior == EstadoDeAprobacion.PENDIENTE
                and self._estado_de_aprobacion != EstadoDeAprobacion.PENDIENTE):
            self.notificar()                            # Dispara Observer solo si hubo cambio real
        return self._estado_de_aprobacion
```

```python
# poo/clases/interfaces/i_sujeto_de_evaluacion.py (mecánica del Observer)
class ISujetoDeEvaluacion(metaclass=ABCMeta):
    def __init__(self):
        self._observadores = []

    def anexar(self, observador):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def notificar(self):
        for observador in self._observadores:
            observador.actualizar(self)     # Cada observador recibe el sujeto completo
```

```python
# poo/clases/servicios/observadores_de_evaluacion.py (observador concreto)
class ObservadorEstadoEstudiante(IObservadorDeEvaluacion):
    def actualizar(self, evaluacion_academica):
        estudiante = evaluacion_academica.estudiante
        estado_final = evaluacion_academica._estado_de_aprobacion
        print(f"[Observer] Estudiante: {estudiante.nombres} {estudiante.apellidos} "
              f"({estudiante.identificacion}). Estado en "
              f"{evaluacion_academica.unidad_curricular.nombre}: {estado_final.value}")
```

## 3.7 Paso 7 — Strategy para evaluación de desempeño docente

`EvaluacionDeDesempeno` no calcula el puntaje por sí misma: delega al contrato
`IEstrategiaDeEvaluacion`, de manera que el criterio de ponderación pueda cambiarse (por
ejemplo, una universidad podría exigir más peso a la evaluación estudiantil que a las horas
cumplidas) sin tocar la entidad.

```python
# poo/clases/evaluacion_de_desempeno.py (fragmento clave)
class EvaluacionDeDesempeno:
    def procesar_evaluacion(self, estrategia: IEstrategiaDeEvaluacion) -> float:
        self._puntaje_final = estrategia.calcular_ponderacion(
            self._porcentaje_de_horas_cumplidas,
            self._entrega_oportuna_de_calificaciones,
            self._porcentaje_de_aprobacion_paralelo,
            self._resultado_de_evaluacion_estudiantil
        )
        return self._puntaje_final
```

```python
# poo/clases/servicios/estrategia_de_evaluacion_estandar.py (implementación concreta)
class EstrategiaDeEvaluacionEstandar(IEstrategiaDeEvaluacion):
    def calcular_ponderacion(self, horas, notas, aprobacion, evaluacion_estudiantil) -> float:
        calculo_horas = horas * self._porcentaje_horas
        calculo_aprobacion = aprobacion * self._porcentaje_aprobacion
        calculo_estudiantes = evaluacion_estudiantil * self._porcentaje_evaluacion_estudiantil
        calculo_notas = self._porcentaje_notas if notas else 0.0   # Criterio binario
        return round(calculo_horas + calculo_notas + calculo_aprobacion + calculo_estudiantes, 2)
```

## 3.8 Paso 8 — Strategy para depuración/validación de la MTN (interoperabilidad)

Para resolver el problema normativo descrito en la sección 2 del documento del proyecto
("registros no estandarizados", "inconsistencias en la estructuración de la oferta
académica"), el equipo separó cada regla de validación en un `ICriterioFiltro` independiente,
de modo que el `DepuradorDeSincronizacion` pueda aplicar cualquier combinación de criterios sin
cambiar su propio código (OCP).

```python
# poo/clases/criterios_filtro/criterio_cedula_formato.py
class CriterioCedulaFormato(ICriterioFiltro):
    def es_valido(self, registro: dict):
        tipo = self._normalizar(registro.get("tipo_de_identificacion", ""))
        numero_de_cedula = str(registro.get("cedula", ""))
        if tipo != "cedula":
            return True                      # Si no es cédula, esta regla no aplica
        return numero_de_cedula.isdigit() and len(numero_de_cedula) == 10
```

```python
# poo/clases/servicios/depurador_de_sincronizacion.py (fragmento clave)
class DepuradorDeSincronizacion:
    def __init__(self, criterios: list):
        self._criterios = criterios           # Lista de ICriterioFiltro (inyección de estrategias)
        self._registros_validos = []
        self._registros_con_observaciones = []

    def procesar_matriz_externa(self, matriz_externa: list):
        for registro in matriz_externa:
            es_valido = True
            for criterio in self._criterios:
                if not criterio.es_valido(registro):
                    es_valido = False
                    break                      # fail-fast: se detiene en el primer criterio que falla
            (self._registros_validos if es_valido else self._registros_con_observaciones).append(registro)
```

Este servicio es la traducción directa, en código, del punto "Sincronización y normalización
de datos" (funcionalidad 1 de "Estructuración y configuración de la oferta académica") del
documento del proyecto: los registros no compatibles quedan "aislados para su revisión
administrativa" — exactamente el comportamiento de `registros_con_observaciones`.

## 3.9 Paso 9 — Algoritmo de distribución de estudiantes

```python
# poo/clases/servicios/distribuidor_de_estudiantes.py (fragmento clave)
class DistribuidorDeEstudiantes:
    def distribuir(self, lista_estudiantes: list) -> list:
        estudiantes_no_asignados = []
        for estudiante in lista_estudiantes:
            mejor_paralelo = self._encontrar_mejor_paralelo()
            if mejor_paralelo:
                mejor_paralelo.vincular_estudiante(estudiante)
            else:
                estudiantes_no_asignados.append(estudiante)
        return estudiantes_no_asignados

    def _encontrar_mejor_paralelo(self):
        """Criterio de balanceo: entre los paralelos con cupo, elige el de MENOR ocupación."""
        paralelos_con_cupo = [p for p in self._paralelos if p.tiene_cupo_disponible()]
        if not paralelos_con_cupo:
            return None
        return min(paralelos_con_cupo, key=lambda p: p.total_estudiantes_matriculados)
```

Este algoritmo resuelve el requerimiento "distribución proporcional y disponibilidad" del
punto 4 de "Estructuración de paralelos y distribución académica" en el documento del
proyecto.

## 3.10 Paso 10 — Monitoreo normativo de plazos (alertas)

```python
# poo/clases/servicios/monitor_normativo.py (fragmento clave)
class MonitorNormativo:
    UMBRAL_PREVENTIVO_DIAS = 5

    def evaluar_proximidad_vencimiento(self, periodo_de_nivelacion, fecha_limite) -> dict:
        dias_restantes = (fecha_limite - date.today()).days
        estado = self._obtener_estado_de_alerta(dias_restantes)
        return {"Periodo de nivelación": periodo_de_nivelacion.periodo,
                "Días restantes": dias_restantes, "Estado de alerta": estado.value}

    def _obtener_estado_de_alerta(self, dias_restantes: int) -> EstadoDeAlerta:
        if dias_restantes < 0:
            return EstadoDeAlerta.CRITICO
        if dias_restantes <= self.UMBRAL_PREVENTIVO_DIAS:
            return EstadoDeAlerta.PREVENTIVO
        return EstadoDeAlerta.NORMAL
```

Esto implementa el punto 3 ("Control de cumplimiento normativo") de "Informe general y
cumplimiento del marco legal": alertas preventivas sobre fechas límite y notificación de
requerimientos pendientes.

## 3.11 Paso 11 — `InformeGeneral` y `ProcesadorDeInforme`

```python
# poo/clases/informe_general.py (fragmento clave)
class InformeGeneral(IInformeInstitucional):
    def emitir_informe_de_nivelacion(self) -> bool:
        """Solo se puede emitir el informe si el periodo académico ya está CERRADO,
        lo cual impide generar el Informe General antes de que termine la nivelación."""
        if self._periodo_academico.estado != EstadoDePeriodo.CERRADO:
            return False
        self._fecha_de_emision = date.today()
        self._estado_de_informe = EstadoDeInforme.REVISION
        return True

    def estimar_tasas_de_aprobacion(self, evaluaciones: list) -> dict:
        total = len(evaluaciones)
        if total == 0:
            return {"tasa_aprobacion": 0.0, "tasa_reprobacion": 0.0, "tasa_retiros": 0.0}
        aprobados = sum(1 for e in evaluaciones if e._estado_de_aprobacion == EstadoDeAprobacion.APROBADO)
        reprobados = sum(1 for e in evaluaciones if e._estado_de_aprobacion == EstadoDeAprobacion.REPROBADO)
        retiros = sum(1 for e in evaluaciones if e._estado_de_aprobacion in
                      (EstadoDeAprobacion.RETIRADO, EstadoDeAprobacion.ANULADO))
        return {"tasa_aprobacion": round(aprobados / total * 100, 2),
                "tasa_reprobacion": round(reprobados / total * 100, 2),
                "tasa_retiros": round(retiros / total * 100, 2)}
```

`ProcesadorDeInforme` es, por diseño, un *stub* consciente: sus métodos `_generar_archivo_pdf`
y `_generar_archivo_excel` devuelven `True` simulando la creación del archivo, porque el
propio código documenta que "en producción, la generación real se maneja en Django
`services.py` usando librerías como ReportLab/openpyxl". Es una decisión correcta de
arquitectura: la capa POO no debe saber escribir archivos en disco; solo debe decidir *si*
corresponde exportar y *en qué formato*.

## 3.12 Paso 12 — El Facade: `CentroDeOperacionAcademica`

Este es el último objeto construido, porque depende de casi todas las clases anteriores. Es el
único punto de entrada que la capa Django necesita conocer para operar sobre 7 subsistemas
del dominio, ocultando los detalles de cada uno:

```python
# poo/clases/servicios/centro_de_operacion_academica.py (fragmento clave)
class CentroDeOperacionAcademica:
    def __init__(self):
        self._distribuidor = DistribuidorDeEstudiantes([])
        self._procesador = ProcesadorDeInforme()

    def registrar_evaluacion(self, evaluacion, parcial_1, parcial_2, porcentaje_asistencia):
        """
        Orquesta en un solo llamado el flujo completo de calificación:
        registrar notas -> registrar asistencia -> calcular nota final ->
        verificar aprobación (que a su vez dispara Chain of Responsibility + Observer).
        Django solo necesita llamar a este único método.
        """
        evaluacion.registrar_calificacion(1, parcial_1)
        evaluacion.registrar_calificacion(2, parcial_2)
        evaluacion.registrar_asistencia_final(porcentaje_asistencia)
        evaluacion.calcular_nota_final()
        return evaluacion.verificar_aprobacion()

    def distribuir_estudiantes(self, paralelos: list, estudiantes: list) -> list:
        self._distribuidor.paralelos = paralelos
        return self._distribuidor.distribuir(estudiantes)
```

## 3.13 Integración con Django: cómo se consume la capa POO

Aunque el alcance de este informe es `poo/`, es importante documentar el punto de contacto,
porque confirma que la capa cumple su propósito de diseño. Una búsqueda en el código (`grep
"from poo"`) muestra que **20 archivos de Django** importan directamente clases de `poo.clases`,
concentrados en `academico/services.py`, `academico/views/*.py`, `usuarios/services.py` y
`usuarios/views/*.py`. Ningún modelo Django (`models.py`) reimplementa una regla de negocio que
ya exista en `poo/`; en su lugar, las vistas y servicios de Django instancian el objeto POO
correspondiente (por ejemplo, un `PeriodoDeNivelacion` a partir de una fila de la base de
datos), invocan sus métodos de validación/comportamiento, y solo entonces persisten el
resultado. Esto es la aplicación práctica del **Principio de Inversión de Dependencias**: la
capa de infraestructura (Django) depende de la capa de dominio (POO), y no al revés.



---

# PARTE 4 — CONCLUSIONES Y ANÁLISIS

## 4.1 Verificación práctica de la capa

Para confirmar que la capa POO es funcional y no solo código estático, se instanció
directamente una de sus entidades en un entorno aislado:

```python
>>> from poo.clases.universidad import Universidad
>>> u = Universidad("Uleam", "ULEAM", "1234")
>>> print(u)
Uleam (ULEAM)
>>> u.validar_datos_de_registro()
{}
```

La importación y ejecución fueron exitosas sin necesidad de Django ni de una base de datos
activa, lo que valida el objetivo de diseño más importante de esta capa: **el dominio de
negocio de NIVEC es independiente de la infraestructura que lo sirve**.

## 4.2 Cómo la capa POO responde a la problemática planteada en la definición del proyecto

- **Registros no estandarizados / inconsistencias en la oferta académica** (sección 2 del
  documento) → resuelto con el patrón Strategy en `criterios_filtro/` y el servicio
  `DepuradorDeSincronizacion`, que aíslan automáticamente los registros que no cumplen el
  formato esperado (p. ej. cédulas mal formadas) sin bloquear el resto del proceso.
- **Solapamientos horarios y desajustes en la distribución de estudiantes** → resueltos con
  `Paralelo.validar_nuevo_horario()`, `Horario.verificar_conflicto_horario()`,
  `Docente.validar_asignacion_a_paralelo()` y `DistribuidorDeEstudiantes`, que en conjunto
  garantizan que ningún paralelo exceda su capacidad, que ningún horario se solape y que
  ningún docente reciba una carga incompatible con su disponibilidad o su tope de horas.
- **Falta de interoperabilidad en la consolidación de rendimiento** → resuelto con
  `EvaluacionAcademica` (Chain of Responsibility + Observer), que centraliza en un único
  flujo verificable las tres reglas normativas de aprobación (estado, asistencia,
  calificación), evitando que la lógica de aprobación quede dispersa o duplicada.
- **Plazos legales para el Informe General** (Art. 67 de la normativa) → resuelto con
  `MonitorNormativo` (alertas preventivas/críticas) e `InformeGeneral` (que impide emitir el
  informe si el periodo no está formalmente cerrado, evitando reportes prematuros o
  incompletos).

## 4.3 Dificultades encontradas durante el desarrollo y cómo se resolvieron

1. **Compatibilidad de sintaxis con Python 3.9.**
   *Dificultad:* al usar *type hints* modernos como `Tipo | None` (sintaxis de unión
   introducida en Python 3.10), el código fallaba en el entorno de despliegue configurado
   para 3.9.
   *Solución:* se estandarizó el uso de `typing.Optional[Tipo]` en toda la capa (ver
   `horario.py`), documentado explícitamente como tarea de "Mejoras a la capa POO" en el
   plan de trabajo del Sprint 1.

2. **Ausencia de archivos `__init__.py` en `poo/` y `poo/clases/`.**
   *Dificultad:* al mover la carpeta original `clases/` a `poo/clases/` (según el plan de
   trabajo), todos los imports (`from clases.xxx import ...`) debían actualizarse a
   `from poo.clases.xxx import ...` en decenas de archivos, con riesgo de romper referencias
   cruzadas entre clases del propio dominio (por ejemplo, `Docente` importa `Horario`, que a
   su vez importa una interfaz).
   *Solución:* se verificó la resolución de imports ejecutando pruebas puntuales de
   importación (`from poo.clases.universidad import Universidad`) confirmando que Python
   resuelve el paquete como *namespace package* implícito sin necesidad de `__init__.py`,
   evitando así trabajo adicional de empaquetado.

3. **Cómo aplicar "sobrecarga de métodos" en un lenguaje que no la soporta nativamente.**
   *Dificultad:* la asignatura exige demostrar sobrecarga, pero Python no permite declarar
   dos métodos con el mismo nombre y distinta firma (a diferencia de Java/C#).
   *Solución:* se adoptó el patrón idiomático de Python con `*args` e inspección de tipos en
   tiempo de ejecución, implementado en `EvaluacionAcademica.registrar_calificacion()` (dos
   formas de invocación: parcial específico o ambos parciales) y en
   `MallaCurricular.agregar_unidad_curricular()` (una unidad, una lista, o varios argumentos).

4. **Evitar que la lógica de aprobación se convirtiera en una cadena de `if/elif` frágil.**
   *Dificultad:* la normativa define un orden de prioridad estricto entre las causales de
   reprobación (estado administrativo > asistencia > calificación), y agregar una nueva regla
   en el futuro (por ejemplo, una causal disciplinaria) habría implicado modificar un método
   monolítico cada vez.
   *Solución:* se aplicó Chain of Responsibility, de modo que cada regla vive en su propio
   manejador (`ManejadorEstadoInactivo`, `ManejadorAsistencia`, `ManejadorCalificacion`) y
   nuevas reglas se insertan en la cadena sin modificar las existentes (cumpliendo OCP).

5. **Cálculo del límite de horas sincrónicas semanales sin acoplarlo a una clase específica.**
   *Dificultad:* la regla de las 20 horas semanales (basada en la jornada nocturna, la más
   restrictiva) no pertenece naturalmente a `MallaCurricular` ni a `Paralelo`, sino que es una
   política normativa transversal que ambas clases (y `services.py` en Django) necesitan
   consultar.
   *Solución:* se extrajo a un módulo de funciones puras (`franja_horaria.py`) en lugar de una
   clase, documentando explícitamente la razón (SRP: es configuración estática, no una
   entidad con estado), evitando así una dependencia circular entre `MallaCurricular` y
   `Paralelo`.

6. **Separar responsabilidades entre "decidir" (POO) y "ejecutar I/O" (Django).**
   *Dificultad:* existía el riesgo de que la capa POO terminara escribiendo archivos Excel o
   consultando la base de datos directamente, lo cual habría roto su independencia y
   dificultado las pruebas.
   *Solución:* servicios como `ProcesadorDeInforme` se diseñaron deliberadamente como *stubs*
   que devuelven `True`/`False` simulando el resultado, dejando la responsabilidad real de
   generar archivos a `django/academico/services.py` (con `openpyxl`), documentado
   explícitamente en el código fuente.

## 4.4 Fortalezas del diseño actual

- Cobertura completa de los cuatro componentes de alcance del proyecto (A, B, C, D) con
  clases de dominio dedicadas.
- Uso disciplinado de 5 patrones de diseño con propósito real (no decorativos): cada patrón
  resuelve un problema concreto identificado en la normativa o en el flujo académico.
- Aplicación verificable de los 5 principios SOLID, con evidencia localizable en archivos
  específicos.
- Separación estricta entre lógica de negocio (POO) e infraestructura (Django), lo que
  permite que la capa POO se pueda probar de forma unitaria sin base de datos ni servidor web.

## 4.5 Aspectos pendientes o parcialmente implementados (auto-documentados en el código)

El propio código señala honestamente sus límites de alcance actual:

- `IncidenciaAcademica` está marcada en su docstring como "Pendiente de implementación
  completa en Django" (el modelo Django ya existe, pero la integración desde vistas es
  incompleta).
- `InformeGeneral.agregar_cohorte_de_matricula()`,
  `consolidar_estadisticas_institucionales()` y `estimar_tasas_de_aprobacion()` están
  señaladas como "para futura implementación" en cuanto a su uso pleno desde la interfaz.
- `ProcesadorDeInforme` genera archivos simulados (`return True`) a la espera de que la
  exportación real se complete en la capa Django.

Estos puntos no representan errores, sino el estado real y transparente del desarrollo a la
fecha de este informe, consistente con un proyecto académico organizado en sprints
incrementales (ver `PLAN_DE_TRABAJO.md`, Sprints 1 a 3).

## 4.6 Conclusión general

La capa `poo/` cumple el rol de **núcleo de dominio** del sistema NIVEC: encapsula en 63
archivos y aproximadamente 3.900 líneas de código todas las reglas de negocio derivadas
directamente de la normativa de nivelación (SENESCYT y reglamento interno ULEAM), aplicando
de manera consistente los pilares de la Programación Orientada a Objetos (abstracción,
encapsulación, herencia, polimorfismo) junto con cinco patrones de diseño reconocidos
(Facade, Prototype, Chain of Responsibility, Observer, Strategy) y los cinco principios SOLID.
El resultado es un modelo de dominio desacoplado de Django, verificable de forma aislada, y
que traduce fielmente cada requerimiento normativo (validación de partícipes, distribución de
paralelos, carga docente, evaluación académica y generación de informes) en comportamiento de
objetos concretos y comprobables.

---

## Anexo — Metodología de trabajo en equipo aplicada al desarrollo de esta capa

Según `PLAN_DE_TRABAJO.md`, la capa POO fue tratada como un entregable propio dentro del
Sprint 1 ("POO / Mejoras", Persona 4), con instrucciones explícitas de: mover `clases/` a
`poo/clases/`, actualizar todos los imports, agregar propiedades y validaciones a las
entidades base, crear `franja_horaria.py`, y corregir la compatibilidad con `Optional` en
lugar de la sintaxis `| None`. Posteriormente, en el Sprint 3 ("Informes", Persona 4), la
misma persona fue responsable de integrar `ProcesadorDeInforme`, `InformeGeneral` y el Facade
`CentroDeOperacionAcademica` con las vistas Django de generación de informes, cerrando el
ciclo entre el dominio puro y su consumo en la aplicación web.
