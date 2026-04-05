# IdeaTracker v1.3.0

Aplicación de escritorio para **registrar, gestionar, priorizar y hacer seguimiento de ideas, planes de negocio y tareas**. Funciona completamente offline, sin bases de datos externas ni conexión a internet.

Desarrollada para **Ubuntu 24.04 LTS** con Python, GTK4 y Libadwaita, siguiendo las guías de diseño GNOME HIG.

---

## Novedades en v1.3.0 — Migración GTK4 + Libadwaita

La versión 1.3.0 es una reescritura completa de la interfaz gráfica, migrando de **PyQt6** a **GTK4 + Libadwaita** y adoptando las guías de diseño GNOME HIG (Human Interface Guidelines).

### Cambios principales

**Arquitectura de navegación**
- Reemplazado el sidebar azul oscuro personalizado por `AdwViewSwitcher` nativo en la barra de título, con tres vistas principales: Ideas, Tareas y Reportes.
- La Configuración se movió a una `AdwPreferencesWindow` accesible desde el menú ⋮ o con `Ctrl+,`.

**Listas de datos**
- Reemplazadas las tablas (`QTableWidget`) por `Gtk.ListBox` con estilo `boxed-list` y `AdwActionRow`, siguiendo el patrón nativo GNOME.
- Cada fila muestra badges de color para prioridad y estatus usando variables de color de Adwaita (se adaptan automáticamente a modo claro/oscuro).
- Botones de editar y eliminar directamente en cada fila, con íconos simbólicos.

**Estados vacíos**
- Implementado `AdwStatusPage` en todas las listas para mostrar un mensaje descriptivo cuando no hay datos, eliminando las pantallas en blanco.

**Eliminación con deshacer**
- Al eliminar una idea o tarea, el elemento desaparece inmediatamente y aparece un `AdwToast` con botón "Deshacer" durante 5 segundos. Si el usuario deshace, el elemento se restaura sin pérdida de datos.

**Búsqueda**
- `GtkSearchBar` ocultable en cada vista, activado con el botón de lupa o `Ctrl+F`.

**Formularios**
- Reemplazados los diálogos `QDialog` por ventanas secundarias `Adw.Window` con `AdwPreferencesGroup`, `AdwEntryRow`, `AdwComboRow` y `AdwSpinRow`.
- Validación con mensajes de error inline via `AdwToast`.

**Configuración**
- Gestión de categorías migrada a `Adw.PreferencesWindow`.
- Confirmaciones de edición y eliminación con `AdwMessageDialog`.

**Reportes rediseñados**
- Cada tipo de reporte tiene ahora dos botones independientes:
  - **Ver reporte**: abre un visor nativo GTK4 con todos los datos como widgets Adwaita (maximizable, scrollable, sin PDF).
  - **Generar PDF**: abre directamente el diálogo de guardado para elegir ubicación y nombre del archivo.
- El visor nativo muestra expandidores, badges de estatus, resúmenes por categoría y secciones colapsables, sin depender de `pdf2image` ni `poppler`.

**Atajos de teclado estándar GNOME**

| Acción | Atajo |
|---|---|
| Nueva idea / tarea | `Ctrl+N` |
| Buscar | `Ctrl+F` |
| Configuración | `Ctrl+,` |
| Atajos de teclado | `Ctrl+?` |
| Actualizar lista | `F5` |
| Salir | `Ctrl+Q` |

**Ícono de aplicación**
- Corregido el ícono en barra de tareas y dock en entornos Wayland (GNOME Shell).
- `application_id` alineado con el nombre del `.desktop` file (`fox.IdeaTracker`) para que GNOME Shell resuelva correctamente el ícono.
- Registro automático del ícono en el tema GTK al iniciar la aplicación.

**Modo oscuro / claro**
- La interfaz respeta automáticamente la preferencia del sistema gracias a `AdwStyleManager`. No requiere configuración manual.

---

## Funcionalidades

### Gestión de Ideas (CRUD completo)
- **Crear** nuevas ideas con todos sus campos: nombre, descripción, origen, fechas, costo aproximado, beneficio esperado, categoría y prioridad.
- **Ver y editar** cualquier idea. La fecha de registro es inmutable una vez creada.
- **Eliminar** con opción de deshacer inmediata (toast con botón "Deshacer").
- **Buscar** ideas por nombre con filtrado en tiempo real.
- Filtros por categoría, prioridad, estatus y mes de registro.
- Ordenamiento por fecha, prioridad o nombre.
- En la edición de una idea se muestran las **tareas asociadas** y se pueden agregar nuevas tareas vinculadas directamente.

### Semáforo de Estatus (Ideas)

| Badge | Estatus | Descripción |
|---|---|---|
| Azul | Por iniciar | Registrada, aún no comenzada |
| Amarillo | Iniciado | Se dieron los primeros pasos |
| Naranja | En proceso | Activamente en desarrollo |
| Verde | Finalizado | Completada exitosamente |
| Gris | Postergado | Pausada temporalmente |
| Rojo | Cancelado | Descartada definitivamente |

### Gestión de Tareas (CRUD completo)
- **Crear** tareas con nombre, descripción y opcionalmente asociarlas a una idea existente.
- **Ver y editar** cualquier tarea. Incluye historial de cambios de estatus (acumulativo e inmutable).
- **Eliminar** con opción de deshacer.
- **Agregar notas** en cualquier momento con fecha y hora automática.
- Filtros por estatus y proyecto asociado.

### Semáforo de Estatus (Tareas)

| Badge | Estatus |
|---|---|
| Azul | Por iniciar |
| Amarillo | Iniciada |
| Verde | Finalizada |
| Gris | Cerrada |

### Notas y Observaciones
- Agrega notas a cualquier **idea** o **tarea** en cualquier momento.
- Cada nota queda registrada con **fecha y hora automática**.
- El historial es **acumulativo**: no se pueden editar ni borrar.

### Configuración de Categorías
- Crea, edita y elimina categorías personalizadas.
- Límite máximo de **10 categorías activas**.
- Al renombrar una categoría, **todas las ideas asociadas se actualizan automáticamente**.
- Al eliminar una categoría, las ideas conservan el nombre anterior como referencia histórica.

Categorías predeterminadas:
`Planes de Negocio` · `Compras` · `Finanzas` · `Viajes` · `Tecnología` · `Personal` · `Operaciones` · `Comercial` · `Educación` · `Otros`

### Reportes
Tres tipos de reportes con **visor nativo** y generación de **PDF independiente**:

- **Reporte Detallado por Idea**: ficha completa con todos los campos, historial de notas y badge de estatus.
- **Reporte Mensual**: listado de ideas del mes con expandidores por idea y resumen de conteo por estatus.
- **Reporte Detallado de Tarea**: ficha completa con historial de cambios de estatus y notas.

---

## Almacenamiento

La app no usa ninguna base de datos externa. Todo se guarda localmente:

```
~/IdeaTracker/
├── data/          ← Un archivo .json por idea
├── tareas/        ← Un archivo .json por tarea
├── exports/       ← PDFs generados
└── config.json    ← Categorías y configuración
```

La carpeta se crea automáticamente en el primer uso.

---

## Instalación y Uso

### Requisitos
- Ubuntu 24.04 LTS (o cualquier distro con GNOME 46+ / libadwaita 1.5+)
- Python 3.12 o superior
- GTK4 + Libadwaita (incluidos en Ubuntu 24.04)

### Instalar dependencias del sistema

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
```

### Instalar dependencias Python y ejecutar

```bash
# Clonar el repositorio
git clone https://github.com/ymontenegr/IdeaTracker.git
cd IdeaTracker

# Instalar dependencias Python
pip install -r requirements.txt --break-system-packages

# Ejecutar
python3 main.py
```

### Dependencias Python

| Paquete | Uso |
|---|---|
| `PyGObject` | Bindings Python para GTK4 + Libadwaita |
| `reportlab` | Generación de PDFs |
| `pdf2image` | Opcional: vista previa de PDFs (no requerido para el visor nativo) |

> Para la generación de PDF con vista previa también se puede instalar `poppler-utils`:
> ```bash
> sudo apt install poppler-utils
> pip install pdf2image
> ```

### Ícono en el escritorio y barra de tareas

Para que el ícono aparezca correctamente en el dock de Ubuntu/Wayland:

```bash
# Instalar ícono en el tema del usuario
mkdir -p ~/.local/share/icons/hicolor/256x256/apps
mkdir -p ~/.local/share/icons/hicolor/scalable/apps
cp AppDir/usr/share/icons/hicolor/256x256/apps/IdeaTracker.png \
   ~/.local/share/icons/hicolor/256x256/apps/
cp AppDir/usr/share/icons/hicolor/scalable/apps/IdeaTracker.svg \
   ~/.local/share/icons/hicolor/scalable/apps/

# Instalar el .desktop file
cp assets/IdeaTracker.desktop ~/.local/share/applications/fox.IdeaTracker.desktop
# Editar la ruta Exec= con la ruta real del proyecto

update-desktop-database ~/.local/share/applications/
```

---

## Tecnologías

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Interfaz gráfica | GTK4 + Libadwaita (PyGObject) |
| Guías de diseño | GNOME HIG |
| Generación de PDF | ReportLab |
| Almacenamiento | Archivos JSON locales |

---

## Estructura del Proyecto

```
IdeaTracker/
├── main.py                  ← Punto de entrada (Adw.Application + CSS global)
├── requirements.txt         ← Dependencias Python
├── assets/
│   ├── IdeaTracker.svg      ← Ícono de la aplicación
│   ├── IdeaTracker.png      ← Ícono PNG
│   └── IdeaTracker.desktop  ← Entrada de menú para Linux
├── AppDir/                  ← Recursos para distribución AppImage
└── src/
    ├── config.py            ← Rutas, constantes y valores por defecto
    ├── models.py            ← Modelos de datos (Idea, Tarea, Nota, Categoria)
    ├── data_manager.py      ← Operaciones CRUD sobre archivos JSON
    ├── pdf_generator.py     ← Generación de reportes con ReportLab
    └── ui/
        ├── main_window.py   ← Ventana principal con AdwViewSwitcher
        ├── ideas_widget.py  ← Lista de ideas (boxed-list + StatusPage + Toast undo)
        ├── idea_form.py     ← Formulario crear/editar idea (Adw.Window)
        ├── tareas_widget.py ← Lista de tareas (boxed-list + StatusPage + Toast undo)
        ├── tarea_form.py    ← Formulario crear/editar tarea (Adw.Window)
        ├── config_widget.py ← Gestión de categorías (AdwPreferencesWindow)
        ├── reports_widget.py← Módulo de reportes (ver + generar PDF)
        ├── report_view.py   ← Visor nativo GTK4 de reportes
        └── pdf_preview.py   ← Guardado de PDF con Gtk.FileDialog
```

---

## Historial de versiones

### v1.3.0 (2026-04-05)
- Migración completa de la interfaz de PyQt6 → GTK4 + Libadwaita
- Navegación con `AdwViewSwitcher` (sin sidebar personalizado)
- Listas con `Gtk.ListBox` `boxed-list` + `AdwActionRow` (reemplaza tablas)
- `AdwStatusPage` en todas las vistas para estados vacíos
- Eliminación con deshacer vía `AdwToast` (5 segundos)
- `GtkSearchBar` para búsqueda con `Ctrl+F`
- Formularios como `Adw.Window` con `AdwPreferencesGroup`
- Configuración migrada a `Adw.PreferencesWindow`
- Reportes: visor nativo GTK4 + botón "Generar PDF" independiente
- Atajos de teclado estándar GNOME (`Ctrl+N`, `Ctrl+F`, `Ctrl+,`, `Ctrl+?`, `F5`, `Ctrl+Q`)
- Soporte automático de modo oscuro/claro via `AdwStyleManager`
- Corrección del ícono en barra de tareas Wayland (app-id `fox.IdeaTracker`)

### v1.2.0
- Vista previa de PDF en pantalla antes de descargar
- Diálogo nativo del sistema para guardar archivos
- Reporte detallado de tarea con historial de estatus
- Confirmación personalizada al cerrar la aplicación
- Filtro por mes de registro en lista de ideas

### v1.1.0
- Formulario de edición de ideas con sección de tareas vinculadas
- Historial de cambios de estatus en tareas
- Notas en tareas con fecha automática
- Mejoras visuales en tablas y formularios

### v1.0.0
- Versión inicial con gestión de ideas, tareas, categorías y reportes PDF

---

## Licencia

MIT License — libre para usar, modificar y distribuir.
