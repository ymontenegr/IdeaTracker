#!/usr/bin/env python3
"""
IdeaTracker — Entry point
Desktop application for managing ideas and business plans.
GTK4 + Libadwaita (GNOME HIG)
"""

import sys
import os

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")
gi.require_version("Gio", "2.0")

from gi.repository import Gtk, Adw, Gdk, Gio, GLib

sys.path.insert(0, os.path.dirname(__file__))
from src.config import setup_directories

# Establece WM_CLASS=ideaTracker — coincide con StartupWMClass del .desktop file.
# Debe llamarse ANTES de crear GApplication.
GLib.set_prgname("ideaTracker")
GLib.set_application_name("IdeaTracker")


# ── Global CSS ────────────────────────────────────────────────────────────────
# Uses Adwaita palette variables — adapts automatically to light/dark/high-contrast.
APP_CSS = """
.status-badge {
    border-radius: 999px;
    padding: 2px 8px;
    font-weight: bold;
    font-size: 0.8em;
}
.badge-blue    { background-color: @accent_bg_color;      color: @accent_fg_color;      }
.badge-green   { background-color: @success_color;        color: @window_bg_color;      }
.badge-yellow  { background-color: @warning_color;        color: @window_bg_color;      }
.badge-orange  { background-color: #e66100;               color: white;                 }
.badge-red     { background-color: @destructive_bg_color; color: @destructive_fg_color; }
.badge-gray    { background-color: @shade_color;          color: @window_fg_color;      }

.dot-blue   { color: @accent_color;      }
.dot-green  { color: @success_color;     }
.dot-yellow { color: @warning_color;     }
.dot-orange { color: #e66100;            }
.dot-red    { color: @destructive_color; }
.dot-gray   { color: @dim_label_color;   }

.filter-bar {
    border-bottom: 1px solid @borders;
    padding: 6px 12px;
}

.desc-frame {
    border: 1px solid @borders;
    border-radius: 12px;
}

.count-label {
    padding: 4px 12px;
    border-top: 1px solid @borders;
}
"""


class IdeaTrackerApp(Adw.Application):
    def __init__(self):
        super().__init__(
            # Debe coincidir exactamente con el nombre del .desktop file
            # (sin la extensión .desktop).
            # ~/.local/share/applications/fox.IdeaTracker.desktop
            application_id="fox.IdeaTracker",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.connect("activate", self._on_activate)

    def _on_activate(self, app):
        self._load_css()
        self._register_icon()
        from src.ui.main_window import MainWindow
        win = MainWindow(application=app)
        win.present()

    def _register_icon(self):
        """Add the app's own icon directory to the GTK icon theme."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Prefer the hicolor-structured directory (used by AppImage)
        hicolor_dir = os.path.join(base_dir, "AppDir", "usr", "share", "icons")
        if os.path.isdir(hicolor_dir):
            icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
            icon_theme.add_search_path(hicolor_dir)
            return
        # Fallback: register the flat assets/ directory as a 256×256 icon
        assets_dir = os.path.join(base_dir, "assets")
        if os.path.isdir(assets_dir):
            icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
            icon_theme.add_search_path(assets_dir)

    def _load_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_string(APP_CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )


def main():
    setup_directories()
    app = IdeaTrackerApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
