#!/bin/bash
# Instala el ícono y el .desktop file de IdeaTracker en el sistema local.
# Esto hace que el ícono aparezca en la barra de tareas de GNOME/Ubuntu.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

ICON_SRC="$SCRIPT_DIR/assets/IdeaTracker.png"
ICON_DST="$HOME/.local/share/icons/hicolor/256x256/apps/ideaTracker.png"
DESKTOP_SRC="$SCRIPT_DIR/assets/IdeaTracker.desktop"
DESKTOP_DST="$HOME/.local/share/applications/ideaTracker.desktop"

echo "=== Instalando ícono de IdeaTracker ==="

# Generar PNG si no existe
if [ ! -f "$ICON_SRC" ]; then
    echo "  Generando PNG desde SVG..."
    python3 "$SCRIPT_DIR/create_icon.py"
fi

# Instalar ícono
mkdir -p "$(dirname "$ICON_DST")"
cp "$ICON_SRC" "$ICON_DST"
echo "  Ícono instalado en: $ICON_DST"

# Instalar .desktop
mkdir -p "$(dirname "$DESKTOP_DST")"
cp "$DESKTOP_SRC" "$DESKTOP_DST"
chmod +x "$DESKTOP_DST"
echo "  .desktop instalado en: $DESKTOP_DST"

# Actualizar caché de íconos y aplicaciones
update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor/" 2>/dev/null || true

echo ""
echo "✅ Listo. Reinicia la aplicación para ver el ícono en la barra de tareas."
echo "   Si no aparece, cierra sesión y vuelve a iniciarla (o reinicia GNOME Shell)."
