# IdeaTracker v1.2.0

Aplicación de escritorio para **registrar, gestionar, priorizar y hacer seguimiento de ideas, planes de negocio y tareas**. Funciona completamente offline, sin bases de datos externas ni conexión a internet.

Desarrollada para **Ubuntu 24.04 LTS** con Python y PyQt6.

---

## Funcionalidades

### Gestión de Ideas (CRUD completo)
- **Crear** nuevas ideas con todos sus campos: nombre, descripción, origen, fechas, costo aproximado, beneficio esperado, categoría y prioridad.
- **Ver y editar** cualquier idea en cualquier momento. La fecha de registro es inmutable una vez creada.
- **Eliminar** ideas con confirmación previa.
- **Buscar** ideas por nombre con filtrado en tiempo real.
- En la edición de una idea se muestran las **tareas asociadas** y se pueden agregar nuevas tareas vinculadas directamente.

### Semáforo de Estatus (Ideas)
Cada idea tiene un indicador visual de estado que puede cambiarse libremente:

| Color | Estatus | Descripción |
|---|---|---|
| Azul | Por iniciar | Registrada, aún no comenzada |
| Amarillo | Iniciado | Se dieron los primeros pasos |
| Naranja | En proceso | Activamente en desarrollo |
| Verde | Finalizado | Completada exitosamente |
| Gris | Postergado | Pausada temporalmente |
| Rojo | Cancelado | Descartada definitivamente |

### Gestión de Tareas (CRUD completo)
Módulo independiente para registrar y hacer seguimiento de tareas concretas.

- **Crear** tareas con nombre, descripción y opcionalmente asociarlas a una idea existente. Las tareas sin idea asociada quedan en el proyecto "Sin proyecto".
- **Ver y editar** cualquier tarea. Incluye historial de cambios de estatus (inmutable y acumulativo).
- **Eliminar** tareas con confirmación previa.
- **Agregar notas** en cualquier momento. Cada nota queda registrada con fecha y hora automática. El historial de notas es acumulativo y no se puede modificar.

### Semáforo de Estatus (Tareas)

| Color | Estatus |
|---|---|
| Azul | Pendiente |
| Amarillo | En progreso |
| Verde | Completada |
| Rojo | Cancelada |

Cada cambio de estatus queda registrado automáticamente en el **historial de estatus** con fecha y hora.

### Filtros y Ordenamiento
- **Ideas**: filtra por categoría, prioridad, estatus o mes/año de registro. Ordena por fecha, prioridad o nombre.
- **Tareas**: filtra por estatus o por proyecto (idea asociada). Ordena por fecha de creación, estatus o nombre.

### Notas y Observaciones
- Agrega notas a cualquier **idea** o **tarea** en cualquier momento.
- Cada nota queda registrada con **fecha y hora automática**.
- El historial es **acumulativo**: las notas no se pueden editar ni borrar, solo agregar nuevas.

### Configuración de Categorías
- Crea, edita y elimina categorías personalizadas.
- Límite máximo de **10 categorías activas**.
- Al renombrar una categoría, **todas las ideas asociadas se actualizan automáticamente**.
- Al eliminar una categoría, las ideas conservan el nombre anterior como referencia histórica.
- Validación de duplicados (sin distinción de mayúsculas/minúsculas).

Categorías predeterminadas:
`Planes de Negocio` · `Compras` · `Finanzas` · `Viajes` · `Tecnología` · `Personal` · `Operaciones` · `Comercial` · `Educación` · `Otros`

### Reportes en PDF
Tres tipos de reportes con **vista previa en pantalla** antes de descargar. Al guardar, se abre un **explorador de archivos nativo** para que el usuario elija la ubicación y el nombre del archivo:

- **Reporte Detallado por Idea**: hoja de vida completa con todos los campos, tareas asociadas, historial de notas e indicador visual de estatus.
- **Reporte Mensual**: resumen tabular de todas las ideas registradas en un mes/año específico, con estadísticas por estatus.
- **Reporte Detallado de Tarea**: ficha completa de una tarea con su descripción, historial de cambios de estatus y notas.

---

## Almacenamiento

La app no usa ninguna base de datos externa. Todo se guarda localmente:

```
~/IdeaTracker/
├── data/          <- Un archivo .json por idea
├── tareas/        <- Un archivo .json por tarea
├── exports/       <- PDFs generados
└── config.json    <- Categorías y configuración
```

La carpeta se crea automáticamente en el primer uso.

---

## Instalación y Uso

### Requisitos
- Ubuntu 24.04 LTS (o cualquier distro con Python 3.12+)
- Python 3.12 o superior

### Instalar dependencias y ejecutar

```bash
# Clonar el repositorio
git clone https://github.com/ymontenegr/IdeaTracker.git
cd IdeaTracker

# Instalar dependencias
pip install -r requirements.txt --break-system-packages

# Ejecutar
python3 main.py
```

### Dependencias Python

| Paquete | Uso |
|---|---|
| `PyQt6` | Interfaz gráfica |
| `reportlab` | Generación de PDFs |
| `pdf2image` | Vista previa de PDFs en pantalla |

> Para la vista previa de PDFs también se requiere `poppler-utils`:
> ```bash
> sudo apt install poppler-utils
> ```

### Ícono en el escritorio y barra de tareas (opcional)

Para que el ícono aparezca correctamente en Ubuntu/Wayland:

```bash
# Generar el archivo PNG del ícono
python3 create_icon.py

# Instalar el ícono y el archivo .desktop
chmod +x install_icon.sh
./install_icon.sh
```

---

## Generar AppImage (distribución portable)

Para generar un ejecutable portable `.AppImage` que no requiere instalación:

```bash
./build_appimage.sh
```

El script instala automáticamente las dependencias necesarias, empaqueta la app con PyInstaller y genera el archivo `IdeaTracker-1.0-x86_64.AppImage`.

```bash
# Dar permisos y ejecutar
chmod +x IdeaTracker-1.0-x86_64.AppImage
./IdeaTracker-1.0-x86_64.AppImage
```

---

## Tecnologías

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Interfaz gráfica | PyQt6 |
| Generación de PDF | ReportLab |
| Vista previa PDF | pdf2image + poppler |
| Almacenamiento | Archivos JSON locales |
| Distribución | AppImage / PyInstaller |

---

## Estructura del Proyecto

```
IdeaTracker/
├── main.py                  <- Punto de entrada
├── requirements.txt         <- Dependencias Python
├── IdeaTracker.spec         <- Configuración PyInstaller
├── build_appimage.sh        <- Script para generar AppImage
├── create_icon.py           <- Genera PNG del ícono desde SVG
├── install_icon.sh          <- Instala ícono y .desktop en el sistema
├── assets/
│   ├── IdeaTracker.svg      <- Ícono de la aplicación
│   ├── IdeaTracker.png      <- Ícono PNG (generado por create_icon.py)
│   └── IdeaTracker.desktop  <- Entrada de menú para Linux
└── src/
    ├── config.py            <- Rutas, constantes y valores por defecto
    ├── models.py            <- Modelos de datos (Idea, Tarea, Nota, Categoria)
    ├── data_manager.py      <- Operaciones CRUD sobre archivos JSON
    ├── pdf_generator.py     <- Generación de reportes con ReportLab
    └── ui/
        ├── main_window.py   <- Ventana principal y navegación
        ├── ideas_widget.py  <- Lista de ideas con filtros
        ├── idea_form.py     <- Formulario crear/editar idea
        ├── tareas_widget.py <- Lista de tareas con filtros
        ├── tarea_form.py    <- Formulario crear/editar tarea
        ├── config_widget.py <- Gestión de categorías
        ├── reports_widget.py<- Módulo de reportes
        └── pdf_preview.py   <- Vista previa y descarga de PDF
```

---

## Licencia

MIT License — libre para usar, modificar y distribuir.
