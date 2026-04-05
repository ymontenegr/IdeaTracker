import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject

from ..data_manager import (
    load_categories, add_category, edit_category,
    delete_category, get_ideas_count_by_category,
)
from ..config import MAX_CATEGORIES


class PreferencesWindow(Adw.PreferencesWindow):
    """Settings window — accessible via Ctrl+, or ⋮ menu → Configuración."""

    __gsignals__ = {
        "categories-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, parent=None):
        super().__init__(transient_for=parent)
        self.set_title("Configuración")
        self.set_default_size(600, 550)
        self._build_ui()

    # ── Build UI ────────────────────────────────────────────────────────────

    def _build_ui(self):
        page = Adw.PreferencesPage(
            title="Categorías",
            icon_name="preferences-other-symbolic",
        )

        # ── Add new category ──────────────────────────────────────────────
        grp_add = Adw.PreferencesGroup(
            title="Gestión de categorías",
            description=f"Máximo {MAX_CATEGORIES} categorías. "
                        "Al editar un nombre, todas las ideas asociadas se actualizan automáticamente.",
        )

        self.new_cat_row = Adw.EntryRow(title="Nombre de la nueva categoría")
        btn_add = Gtk.Button(icon_name="list-add-symbolic")
        btn_add.add_css_class("flat")
        btn_add.set_tooltip_text("Agregar categoría")
        btn_add.set_valign(Gtk.Align.CENTER)
        btn_add.connect("clicked", self._on_add)
        self.new_cat_row.add_suffix(btn_add)
        self.new_cat_row.connect("entry-activated", self._on_add)
        grp_add.add(self.new_cat_row)

        page.add(grp_add)

        # ── Category list ─────────────────────────────────────────────────
        self._grp_list = Adw.PreferencesGroup()
        self._list_box = Gtk.ListBox()
        self._list_box.add_css_class("boxed-list")
        self._list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self._grp_list.add(self._list_box)
        page.add(self._grp_list)

        self.add(page)
        self._refresh_list()

    # ── List management ─────────────────────────────────────────────────────

    def _refresh_list(self):
        while True:
            child = self._list_box.get_first_child()
            if child is None:
                break
            self._list_box.remove(child)

        cats = load_categories()
        count = len(cats)
        self._grp_list.set_title(f"{count} / {MAX_CATEGORIES} categorías")

        if not cats:
            empty = Adw.ActionRow(title="Sin categorías registradas")
            empty.add_css_class("dim-label")
            self._list_box.append(empty)
            return

        for cat in cats:
            row = self._make_cat_row(cat.id, cat.nombre)
            self._list_box.append(row)

    def _make_cat_row(self, cat_id: str, nombre: str) -> Adw.ActionRow:
        row = Adw.ActionRow(title=nombre)

        btn_edit = Gtk.Button(icon_name="document-edit-symbolic")
        btn_edit.add_css_class("flat")
        btn_edit.set_tooltip_text("Editar nombre")
        btn_edit.set_valign(Gtk.Align.CENTER)
        btn_edit.connect("clicked", lambda _b: self._on_edit(cat_id, nombre))
        row.add_suffix(btn_edit)

        btn_del = Gtk.Button(icon_name="edit-delete-symbolic")
        btn_del.add_css_class("flat")
        btn_del.add_css_class("destructive-action")
        btn_del.set_tooltip_text("Eliminar categoría")
        btn_del.set_valign(Gtk.Align.CENTER)
        btn_del.connect("clicked", lambda _b: self._on_delete(cat_id, nombre))
        row.add_suffix(btn_del)

        return row

    # ── Action handlers ─────────────────────────────────────────────────────

    def _on_add(self, *_):
        nombre = self.new_cat_row.get_text().strip()
        if not nombre:
            self.new_cat_row.add_css_class("error")
            return
        self.new_cat_row.remove_css_class("error")

        success, msg = add_category(nombre)
        if success:
            self.new_cat_row.set_text("")
            self._refresh_list()
            self.emit("categories-changed")
        else:
            # Show error inline on the entry row
            self.new_cat_row.add_css_class("error")
            dialog = Adw.MessageDialog(
                transient_for=self,
                heading="No se pudo agregar",
                body=msg,
            )
            dialog.add_response("ok", "Entendido")
            dialog.present()

    def _on_edit(self, cat_id: str, current_name: str):
        """Inline edit: open a small dialog asking for new name."""
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Editar categoría",
            body=f"Nuevo nombre para «{current_name}»:",
        )

        entry = Gtk.Entry(text=current_name, hexpand=True)
        entry.set_margin_start(12)
        entry.set_margin_end(12)
        entry.set_margin_top(6)
        entry.set_margin_bottom(6)
        dialog.set_extra_child(entry)

        dialog.add_response("cancel", "Cancelar")
        dialog.add_response("save", "Guardar")
        dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("save")
        dialog.set_close_response("cancel")

        def on_response(dlg, response):
            if response == "save":
                nuevo = entry.get_text().strip()
                if not nuevo:
                    return
                success, msg = edit_category(cat_id, nuevo)
                if success:
                    self._refresh_list()
                    self.emit("categories-changed")
                else:
                    err = Adw.MessageDialog(
                        transient_for=self,
                        heading="Error al renombrar",
                        body=msg,
                    )
                    err.add_response("ok", "Entendido")
                    err.present()

        dialog.connect("response", on_response)
        dialog.present()

    def _on_delete(self, cat_id: str, nombre: str):
        count = get_ideas_count_by_category(cat_id)
        body = f"¿Eliminar la categoría «{nombre}»?"
        if count > 0:
            body += (
                f"\n\nHay {count} idea{'s' if count != 1 else ''} asociada{'s' if count != 1 else ''} "
                "a esta categoría. Las ideas no serán eliminadas; conservarán el nombre "
                "anterior como referencia histórica."
            )

        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Eliminar categoría",
            body=body,
        )
        dialog.add_response("cancel", "Cancelar")
        dialog.add_response("delete", "Eliminar")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")

        def on_response(dlg, response):
            if response == "delete":
                delete_category(cat_id)
                self._refresh_list()
                self.emit("categories-changed")

        dialog.connect("response", on_response)
        dialog.present()
