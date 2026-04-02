# 💡 IdeaTracker v1.2.0

Aplicación de escritorio para **registrar, gestionar, priorizar y hacer seguimiento de ideas y planes de negocio**. Funciona completamente offline, sin bases de datos externas ni conexión a internet.

Desarrollada para **Ubuntu 24.04 LTS** con Python y PyQt6.

---

## ✨ Funcionalidades

### 📝 Gestión de Ideas (CRUD completo)
- **Crear** nuevas ideas con todos sus campos: nombre, descripción, origen, fechas, costo aproximado, beneficio esperado, categoría y prioridad.
- **Ver y editar** cualquier idea en cualquier momento. La fecha de registro es inmutable una vez creada.
- **Eliminar** ideas con confirmación previa.
- **Buscar** ideas por nombre con filtrado en tiempo real.

### 🚦 Semáforo de Estatus
Cada idea tiene un indicador visual de estado que puede cambiarse libremente en cualquier momento:

| Color | Estatus | Descripción |
|---|---|---|
| 🔵 Azul | Por iniciar | Registrada, aún no comenzada |
| 🟡 Amarillo | Iniciado | Se dieron los primeros pasos |
| 🟠 Naranja | En proceso | Activamente en desarrollo |
| 🟢 Verde | Finalizado | Completada exitosamente |
| ⚫ Gris | Postergado | Pausada temporalmente |
| 🔴 Rojo | Cancelado | Descartada definitivamente |

### 🗂️ Filtros y Ordenamiento
- Filtra ideas por **categoría**, **prioridad**, **estatus** o **mes/año** de registro.
- Ordena por **fecha** (más reciente o más antigua), **prioridad** o **nombre (A-Z)**.

### 📌 Notas y Observaciones
- Agrega notas a cualquier idea en cualquier momento.
- Cada nota queda registrada con **fecha y hora automática**.
- El historial es **acumulativo**: las notas no se pueden editar ni borrar, solo agregar nuevas.

### ⚙️ Configuración de Categorías
- Crea, edita y elimina categorías personalizadas.
- Límite máximo de **10 categorías activas**.
- Al renombrar una categoría, **todas las ideas asociadas se actualizan automáticamente**.
- Al eliminar una categoría, las ideas conservan el nombre anterior como referencia histórica.
- Validación de duplicados (sin distinción de mayúsculas/minúsculas).

Categorías predeterminadas:
`Planes de Negocio` · `Compras` · `Finanzas` · `Viajes` · `Tecnología` · `Personal` · `Operaciones` · `Comercial` · `Educación` · `Otros`

### 📊 Reportes en PDF
Dos tipos de reportes con **vista previa en pantalla** antes de descargar:

- **Reporte Detallado por Idea**: hoja de vida completa con todos los campos, historial de notas e indicador visual de estatus.
- **Reporte Mensual**: resumen tabular de todas las ideas registradas en un mes/año específico, con estadísticas por estatus.

Los PDFs se guardan en `~/IdeaTracker/exports/` con timestamp para evitar sobrescrituras.

---

## 🗄️ Almacenamiento

La app no usa ninguna base de datos externa. Todo se guarda localmente:

```
~/IdeaTracker/
├── data/          ← Un archivo .json por idea
├── exports/       ← PDFs generados
└── config.json    ← Categorías y configuración
```

La carpeta se crea automáticamente en el primer uso.

---

## 🚀 Instalación y Uso

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

---

## 📦 Generar AppImage (distribución portable)

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

## 🛠️ Tecnologías

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Interfaz gráfica | PyQt6 |
| Generación de PDF | ReportLab |
| Vista previa PDF | pdf2image + poppler |
| Almacenamiento | Archivos JSON locales |
| Distribución | AppImage / PyInstaller |

---

## 📁 Estructura del Proyecto

```
IdeaTracker/
├── main.py                  ← Punto de entrada
├── requirements.txt         ← Dependencias Python
├── IdeaTracker.spec         ← Configuración PyInstaller
├── build_appimage.sh        ← Script para generar AppImage
├── assets/
│   ├── IdeaTracker.svg      ← Ícono de la aplicación
│   └── IdeaTracker.desktop  ← Entrada de menú para Linux
└── src/
    ├── config.py            ← Rutas, constantes y valores por defecto
    ├── models.py            ← Modelos de datos (Idea, Nota, Categoria)
    ├── data_manager.py      ← Operaciones CRUD sobre archivos JSON
    ├── pdf_generator.py     ← Generación de reportes con ReportLab
    └── ui/
        ├── main_window.py   ← Ventana principal y navegación
        ├── ideas_widget.py  ← Lista de ideas con filtros
        ├── idea_form.py     ← Formulario crear/editar idea
        ├── config_widget.py ← Gestión de categorías
        ├── reports_widget.py← Módulo de reportes
        └── pdf_preview.py   ← Vista previa y descarga de PDF
```

---

## 📄 Licencia

MIT License — libre para usar, modificar y distribuir.
