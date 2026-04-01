#!/bin/bash
# ─────────────────────────────────────────────────────────────────
#  IdeaTracker v1.0 — AppImage Builder
#  Genera: IdeaTracker-1.0-x86_64.AppImage
# ─────────────────────────────────────────────────────────────────
set -e

APP_NAME="IdeaTracker"
APP_VERSION="1.0"
ARCH="x86_64"
OUTPUT="${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   IdeaTracker — AppImage Builder  v1.0  ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. Dependencias del sistema ───────────────────────────────────
echo "▶ [1/5] Verificando dependencias del sistema..."

MISSING=""
for pkg in python3 pip3 wget; do
    command -v "$pkg" &>/dev/null || MISSING="$MISSING $pkg"
done
if [ -n "$MISSING" ]; then
    echo "   Instalando:$MISSING"
    sudo apt-get install -y $MISSING
fi

# Convertir SVG a PNG (necesario para el icono del AppImage)
if ! command -v rsvg-convert &>/dev/null && ! command -v inkscape &>/dev/null && ! command -v convert &>/dev/null; then
    echo "   Instalando librsvg2-bin para convertir el ícono..."
    sudo apt-get install -y librsvg2-bin 2>/dev/null || \
    sudo apt-get install -y imagemagick 2>/dev/null || true
fi

# ── 2. Dependencias Python ────────────────────────────────────────
echo "▶ [2/5] Instalando dependencias Python..."
pip install --break-system-packages -q \
    PyQt6 reportlab pdf2image pyinstaller

# ── 3. PyInstaller — generar bundle ──────────────────────────────
echo "▶ [3/5] Empaquetando con PyInstaller..."
rm -rf build dist

pyinstaller IdeaTracker.spec --noconfirm --clean

echo "   Bundle generado en: dist/IdeaTracker/"

# ── 4. Construir AppDir ───────────────────────────────────────────
echo "▶ [4/5] Construyendo AppDir..."

APPDIR="AppDir"
rm -rf "$APPDIR"

# Estructura
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/lib"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/icons/hicolor/scalable/apps"

# Copiar bundle de PyInstaller
cp -r dist/IdeaTracker/* "$APPDIR/usr/bin/"

# Ícono
if command -v rsvg-convert &>/dev/null; then
    rsvg-convert -w 256 -h 256 assets/IdeaTracker.svg > "$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
elif command -v inkscape &>/dev/null; then
    inkscape --export-type=png --export-width=256 --export-height=256 \
        --export-filename="$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png" \
        assets/IdeaTracker.svg
elif command -v convert &>/dev/null; then
    convert -background none -resize 256x256 assets/IdeaTracker.svg \
        "$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
else
    # Fallback: copiar SVG como PNG (algunos sistemas lo aceptan)
    cp assets/IdeaTracker.svg "$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
fi

cp assets/IdeaTracker.svg "$APPDIR/usr/share/icons/hicolor/scalable/apps/${APP_NAME}.svg"

# Symlinks requeridos por AppImage
cp assets/IdeaTracker.desktop "$APPDIR/usr/share/applications/"
cp assets/IdeaTracker.desktop "$APPDIR/${APP_NAME}.desktop"
cp "$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png" "$APPDIR/${APP_NAME}.png" 2>/dev/null || \
cp assets/IdeaTracker.svg "$APPDIR/${APP_NAME}.png"

# AppRun — punto de entrada
cat > "$APPDIR/AppRun" << 'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export QT_PLUGIN_PATH="${HERE}/usr/bin/PyQt6/Qt6/plugins"
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/IdeaTracker" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

echo "   AppDir listo: $APPDIR/"

# ── 5. Descargar appimagetool y generar AppImage ──────────────────
echo "▶ [5/5] Generando AppImage..."

TOOL="appimagetool-x86_64.AppImage"
if [ ! -f "$TOOL" ]; then
    echo "   Descargando appimagetool..."
    wget -q --show-progress \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
        -O "$TOOL"
    chmod +x "$TOOL"
fi

ARCH=x86_64 ./"$TOOL" "$APPDIR" "$OUTPUT"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅  AppImage generado exitosamente:                     ║"
printf  "║     %-54s ║\n" "$OUTPUT"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Para ejecutarlo:                                        ║"
printf  "║     chmod +x %-46s ║\n" "$OUTPUT"
printf  "║     ./%-53s ║\n" "$OUTPUT"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
