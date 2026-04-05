from datetime import datetime

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gio", "2.0")
gi.require_version("GLib", "2.0")

from gi.repository import Gtk, Adw, Gio, GLib

from ..config import EXPORTS_DIR


class PDFPreviewWindow(Adw.Window):
    """
    Shows a PDF preview using rendered page images (via pdf2image / poppler).
    Falls back to a status page notice when rendering is unavailable.
    """

    def __init__(self, pdf_bytes: bytes, suggested_name: str, parent=None):
        super().__init__(transient_for=parent, modal=True)
        self._pdf_bytes = pdf_bytes
        self._suggested_name = suggested_name
        self.set_title("Vista previa — Reporte")
        self.set_default_size(860, 700)
        self.set_size_request(600, 500)
        self._build_ui()
        self._load_preview()

    # ── Build UI ────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._toast_overlay = Adw.ToastOverlay()
        self.set_content(self._toast_overlay)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._toast_overlay.set_child(main_box)

        # Header bar
        header = Adw.HeaderBar()

        btn_close = Gtk.Button(label="Cerrar")
        btn_close.add_css_class("flat")
        btn_close.connect("clicked", lambda _: self.close())
        header.pack_start(btn_close)

        btn_save = Gtk.Button(label="Guardar PDF…")
        btn_save.add_css_class("suggested-action")
        btn_save.set_tooltip_text("Guardar el PDF en disco")
        btn_save.connect("clicked", self._on_save_as)
        header.pack_end(btn_save)

        main_box.append(header)

        # Scrollable preview area
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self._preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._preview_box.set_margin_start(24)
        self._preview_box.set_margin_end(24)
        self._preview_box.set_margin_top(24)
        self._preview_box.set_margin_bottom(24)
        self._preview_box.set_halign(Gtk.Align.CENTER)

        scroll.set_child(self._preview_box)
        main_box.append(scroll)

    # ── Preview rendering ────────────────────────────────────────────────────

    def _load_preview(self):
        try:
            from pdf2image import convert_from_bytes
            import cairo
            from gi.repository import GdkPixbuf

            images = convert_from_bytes(self._pdf_bytes, dpi=120, fmt="ppm")
            for img in images:
                img_rgb = img.convert("RGB")
                data = img_rgb.tobytes()
                w, h = img_rgb.size
                pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                    data,
                    GdkPixbuf.Colorspace.RGB,
                    False,   # has_alpha
                    8,
                    w, h,
                    w * 3,
                )
                picture = Gtk.Picture.new_for_pixbuf(pixbuf)
                picture.set_size_request(w, h)
                picture.add_css_class("card")
                self._preview_box.append(picture)

        except ImportError:
            self._show_fallback()
        except Exception as e:
            self._show_fallback(str(e))

    def _show_fallback(self, detail: str = ""):
        desc = (
            "El reporte está listo para guardarse.\n"
            "Para ver la vista previa instala poppler-utils:\n"
            "  sudo apt install poppler-utils\n"
            "  pip install pdf2image"
        )
        if detail:
            desc += f"\n\nDetalle técnico: {detail}"

        status = Adw.StatusPage(
            icon_name="document-export-symbolic",
            title="Reporte generado",
            description=desc,
        )
        self._preview_box.append(status)

    # ── Save As ──────────────────────────────────────────────────────────────

    def _on_save_as(self, _button):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{self._suggested_name}_{timestamp}.pdf"

        pdf_filter = Gtk.FileFilter()
        pdf_filter.set_name("Archivos PDF")
        pdf_filter.add_mime_type("application/pdf")

        filters = Gio.ListStore(item_type=Gtk.FileFilter)
        filters.append(pdf_filter)

        dialog = Gtk.FileDialog()
        dialog.set_title("Guardar reporte PDF")
        dialog.set_initial_name(default_name)
        dialog.set_filters(filters)

        # Set initial folder to EXPORTS_DIR
        try:
            exports_file = Gio.File.new_for_path(str(EXPORTS_DIR))
            dialog.set_initial_folder(exports_file)
        except Exception:
            pass

        dialog.save(self, None, self._on_save_response)

    def _on_save_response(self, dialog, result):
        try:
            file = dialog.save_finish(result)
            if file is None:
                return
            path = file.get_path()
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            with open(path, "wb") as f:
                f.write(self._pdf_bytes)
            toast = Adw.Toast(title="PDF guardado")
            toast.set_button_label("Abrir carpeta")
            toast.set_action_name("app.open-exports")
            toast.set_timeout(5)
            self._toast_overlay.add_toast(toast)
        except GLib.Error:
            pass  # User cancelled
        except Exception as e:
            toast = Adw.Toast(title=f"Error al guardar: {e}")
            toast.set_timeout(4)
            self._toast_overlay.add_toast(toast)
