# Documento de Requerimientos — IdeaTracker MVP

## 1. Descripción General

**Nombre del proyecto:** IdeaTracker  
**Plataforma:** Aplicación de escritorio — Linux Ubuntu 24.04  
**Objetivo:** Permitir al usuario registrar, gestionar, priorizar y hacer seguimiento de ideas o planes de negocio, sin dependencia de bases de datos externas ni conexión a internet.

---

## 2. Arquitectura y Almacenamiento

- La aplicación es **completamente autosuficiente** (no requiere conexión a internet ni base de datos externa).
- Cada idea se guarda como un **archivo JSON independiente** dentro de una carpeta local del proyecto.
- Las categorías se guardan en el archivo `config.json`.
- El usuario puede **exportar** cualquier archivo JSON en cualquier momento.
- La estructura de carpetas será:

```
~/IdeaTracker/
├── data/           ← Un archivo .json por idea
├── exports/        ← PDFs generados
└── config.json     ← Configuración de la app (incluye categorías)
```

---

## 3. Menú Principal

El menú principal contiene **4 secciones:**

| Opción | Descripción |
|---|---|
| 📝 **Ideas** | CRUD completo de ideas/planes de negocio |
| 📊 **Reportes** | Generación y descarga de reportes en PDF |
| ⚙️ **Configuración** | Gestión de categorías y preferencias generales |
| 🚪 **Salir** | Cierra la aplicación |

---

## 4. Módulo de Ideas (CRUD)

### 4.1 Crear nueva idea

Al registrar una nueva idea, el sistema solicitará los siguientes campos:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| Nombre / Tema | Texto corto | ✅ | Título de la idea |
| Descripción general | Texto largo | ✅ | Explicación del plan o idea |
| Origen de la idea | Texto / Selector | ✅ | De dónde viene la idea (ej. reunión, lectura, conversación, análisis propio, etc.) |
| Fecha de registro | Fecha | ✅ Auto | Se genera automáticamente al crear |
| Fecha probable de inicio | Fecha | ✅ | Estimado de cuándo arrancaría |
| Costo aproximado | Numérico (moneda) | ✅ | Inversión estimada |
| Beneficio esperado | Texto largo | ✅ | Descripción del retorno o valor que generará |
| Categoría | Selector dinámico | ✅ | Cargado desde las categorías definidas en Configuración |
| Prioridad | Selector | ✅ | Alta / Media / Baja |
| Estatus | Semáforo | ✅ Auto | Inicia siempre en "Por iniciar" al crear |
| Notas / Observaciones | Lista de entradas | Opcional | Se agregan en cualquier momento con fecha y hora |

### 4.2 Ver / Editar idea

- El usuario puede buscar y seleccionar cualquier idea existente.
- Todos los campos son editables excepto **Fecha de registro** (es inmutable).
- El campo **Estatus** es editable en cualquier momento y puede cambiarse a cualquier estado sin restricción de orden o flujo. No hay transiciones obligatorias entre estados.
- Si una categoría fue eliminada desde Configuración, la idea conserva el nombre de la categoría anterior como texto plano (no se rompe el registro).
- Se pueden agregar nuevas **notas u observaciones** con timestamp automático, sin borrar las anteriores (historial acumulativo).

### 4.3 Eliminar idea

- Confirmación requerida antes de eliminar.
- Al eliminar se borra el archivo `.json` correspondiente.

### 4.4 Semáforo de Estatus

| Estatus | Color | Descripción |
|---|---|---|
| 🔵 Por iniciar | Azul | La idea está registrada pero no ha comenzado |
| 🟡 Iniciado | Amarillo | Se dieron los primeros pasos |
| 🟠 En proceso | Naranja | Activamente en desarrollo |
| 🟢 Finalizado | Verde | Completado exitosamente |
| ⚫ Postergado | Gris | Pausado temporalmente |
| 🔴 Cancelado | Rojo | Descartado definitivamente |

> El usuario puede asignar cualquier estatus libremente desde el formulario de edición, independientemente del estado actual o el historial del proyecto.

### 4.5 Listado y Organización

- Vista de listado con todas las ideas.
- **Filtros disponibles:** por categoría, por prioridad, por estatus, por mes/año.
- **Ordenamiento:** por fecha de registro, por prioridad, por nombre (A-Z).

---

## 5. Módulo de Configuración

### 5.1 Gestión de Categorías

- El usuario puede **crear, editar y eliminar** categorías personalizadas.
- **Límite máximo: 10 categorías.**
- El sistema viene con las siguientes **categorías predeterminadas** al instalarse por primera vez:

| # | Categoría predeterminada |
|---|---|
| 1 | Planes de Negocio |
| 2 | Compras |
| 3 | Finanzas |
| 4 | Viajes |
| 5 | Tecnología |
| 6 | Personal |
| 7 | Operaciones |
| 8 | Comercial |
| 9 | Educación |
| 10 | Otros |

### 5.2 Reglas de las Categorías

- No se pueden crear dos categorías con el mismo nombre (validación de duplicados, sin distinción de mayúsculas/minúsculas).
- Si se intenta agregar una categoría cuando ya hay 10, el sistema muestra un aviso: *"Has alcanzado el límite de 10 categorías. Elimina una para poder agregar otra."*
- Al **eliminar** una categoría, el sistema advierte si hay ideas asociadas a ella. La eliminación no borra las ideas; estas conservan el nombre de la categoría como texto histórico.
- Al **editar** el nombre de una categoría, el sistema actualiza automáticamente todos los archivos JSON de ideas que la tenían asignada.
- Las categorías se guardan en `config.json` con la siguiente estructura:

```json
{
  "categorias": [
    { "id": "uuid-1", "nombre": "Planes de Negocio" },
    { "id": "uuid-2", "nombre": "Compras" },
    { "id": "uuid-3", "nombre": "Finanzas" },
    { "id": "uuid-4", "nombre": "Viajes" },
    { "id": "uuid-5", "nombre": "Tecnología" },
    { "id": "uuid-6", "nombre": "Personal" },
    { "id": "uuid-7", "nombre": "Operaciones" },
    { "id": "uuid-8", "nombre": "Comercial" },
    { "id": "uuid-9", "nombre": "Educación" },
    { "id": "uuid-10", "nombre": "Otros" }
  ]
}
```

---

## 6. Módulo de Reportes (PDF)

### Flujo general de reportes

1. El reporte se **genera y visualiza primero en pantalla** dentro de la propia aplicación (vista previa integrada).
2. Desde la vista previa, el usuario tiene un botón **"Descargar PDF"** que guarda el archivo en `~/IdeaTracker/exports/` con nombre que incluye timestamp para evitar sobrescrituras.
3. El usuario también puede **cerrar la vista previa** sin descargar si solo quería consultar.

### 6.1 Reporte Detallado por Idea

- El usuario selecciona una idea específica de un listado.
- El reporte incluye:
  - Todos los datos del registro (hoja de vida completa)
  - Categoría asignada
  - Fecha de registro
  - Historial de notas/observaciones con sus fechas
  - Indicador visual de estatus (semáforo con color)

### 6.2 Reporte Mensual de Ideas

- El usuario selecciona el **mes y año** que desea consultar.
- El reporte incluye un resumen tabular con:
  - Fecha de registro
  - Nombre de la idea
  - Categoría
  - Descripción breve
  - Fecha probable de implementación
  - Costo aproximado
  - Beneficio esperado
  - Indicador visual de estatus (semáforo con color)

---

## 7. Estructura del archivo JSON por Idea

```json
{
  "id": "uuid-unico",
  "nombre": "Nombre de la idea",
  "descripcion": "Descripción general...",
  "origen": "Reunión con equipo comercial",
  "fecha_registro": "2026-03-31T10:00:00",
  "fecha_inicio_probable": "2026-06-01",
  "costo_aproximado": 5000.00,
  "beneficio_esperado": "Reducción del 20% en tiempos operativos",
  "categoria_id": "uuid-1",
  "categoria_nombre": "Planes de Negocio",
  "prioridad": "Alta",
  "estatus": "Por iniciar",
  "notas": [
    {
      "fecha": "2026-04-15T09:30:00",
      "texto": "Se presentó al equipo directivo, buena recepción"
    }
  ]
}
```

> **Nota:** Se guarda tanto el `categoria_id` como el `categoria_nombre` para preservar el historial aunque la categoría sea editada o eliminada posteriormente.

---

## 8. Tecnología Sugerida

| Componente | Tecnología recomendada |
|---|---|
| Lenguaje | Python 3.12+ |
| UI (interfaz gráfica) | PyQt6 o CustomTkinter |
| Generación de PDF | ReportLab o WeasyPrint |
| Visor de PDF integrado | QWebEngineView (PyQt6) o renderizado como imagen |
| Almacenamiento | JSON files (sin ORM ni DB) |
| Empaquetado | PyInstaller (genera ejecutable compatible con Ubuntu 24.04) |

---

## 9. Restricciones y Reglas de Negocio

- No se requiere autenticación (app monousuario).
- No se necesita conexión a internet en ningún momento.
- La carpeta de datos y el `config.json` se crean automáticamente en el primer uso.
- No se puede modificar la fecha de registro una vez creado el registro.
- Las notas son acumulativas: no se pueden editar ni borrar, solo agregar nuevas.
- El estatus inicial de toda idea nueva es siempre **"Por iniciar"**.
- El estatus puede cambiarse libremente a cualquier valor en cualquier momento (sin flujo obligatorio).
- Máximo **10 categorías** activas al mismo tiempo.
- Los reportes se visualizan en pantalla antes de decidir si se descargan.
- Los PDFs descargados no sobreescriben anteriores (se nombran con timestamp).

---

## 10. Criterios de Aceptación del MVP

- [ ] La app abre correctamente en Ubuntu 24.04 sin instalaciones adicionales manuales.
- [ ] Se puede crear, ver, editar y eliminar ideas.
- [ ] El selector de categoría en el formulario carga dinámicamente desde `config.json`.
- [ ] El módulo de Configuración permite gestionar hasta 10 categorías con validación de duplicados.
- [ ] El semáforo de estatus cambia visualmente según el estado seleccionado.
- [ ] El estatus se puede cambiar libremente desde el formulario de edición.
- [ ] Se pueden agregar notas con timestamp a cualquier idea.
- [ ] Los reportes se visualizan en pantalla con opción de descarga en PDF.
- [ ] Los PDFs descargados se guardan en `~/IdeaTracker/exports/` con nombre único.
- [ ] Los datos persisten entre sesiones de la aplicación.
- [ ] El botón Salir cierra la aplicación limpiamente.
