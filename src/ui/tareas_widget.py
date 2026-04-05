from datetime import datetime
from typing import List, Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject

from ..data_manager import load_all_tareas, delete_tarea, save_tarea
from ..models import Tarea
from ..config import TAREA_STATUS_LIST, IDEA_DEFAULT_ID, IDEA_DEFAULT_NAME


# ── Status → badge CSS class ──────────────────────────────────────────────────
STATUS_BADGE = {
    "Por iniciar": "badge-blue",
    "Iniciada":    "badge-yellow",
    "Finalizada":  "badge-green",
    "Cerrada":     "badge-gray",
}
STATUS_DOT = {
    "Por iniciar": "dot-blue",
    "Iniciada":    "dot-yellow",
    "Finalizada":  "dot-green",
    "Cerrada":     "dot-gray",
}


class TareasWidget(Gtk.Box):
    def __init__(self, toast_overlay: Adw.ToastOverlay):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._toast_overlay = toast_overlay
        self._all_tareas: List[Tarea] = []
        self._pending_delete: Optional[Tarea] = None

        # idea filter data (ID list parallel to dropdown)
        self._idea_ids: List[Optional[str]] = [None]

        self._build_ui()
        self.refresh()

    # ── Build UI ────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Search bar (Ctrl+F) ──────────────────────────────────────────
        self.search_bar = Gtk.SearchBar()
        self.search_bar.set_show_close_button(True)
        self.search_entry = Gtk.SearchEntry(placeholder_text="Buscar por nombre…")
        self.search_entry.set_hexpand(True)
        self.search_bar.set_child(self.search_entry)
        self.search_bar.connect_entry(self.search_entry)
        self.search_entry.connect("search-changed", lambda _: self._apply_filters())
        self.append(self.search_bar)

        # ── Filter bar ────────────────────────────────────────────────────
        filter_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        filter_bar.add_css_class("filter-bar")
        filter_bar.set_margin_start(12)
        filter_bar.set_margin_end(12)
        filter_bar.set_margin_top(6)
        filter_bar.set_margin_bottom(6)

        self.btn_search = Gtk.ToggleButton(icon_name="system-search-symbolic")
        self.btn_search.set_tooltip_text("Buscar (Ctrl+F)")
        self.btn_search.bind_property(
            "active", self.search_bar, "search-mode-enabled",
            GObject.BindingFlags.BIDIRECTIONAL,
        )
        filter_bar.append(self.btn_search)

        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        sep.set_margin_top(4)
        sep.set_margin_bottom(4)
        filter_bar.append(sep)

        # Status filter
        lbl_est = Gtk.Label(label="Estatus:")
        lbl_est.add_css_class("dim-label")
        filter_bar.append(lbl_est)

        status_items = ["Todos"] + TAREA_STATUS_LIST
        self.filter_est = Gtk.DropDown(
            model=Gtk.StringList.new(status_items), selected=0
        )
        self.filter_est.connect("notify::selected", lambda *_: self._apply_filters())
        filter_bar.append(self.filter_est)

        # Project/Idea filter
        lbl_idea = Gtk.Label(label="Proyecto:")
        lbl_idea.add_css_class("dim-label")
        lbl_idea.set_margin_start(6)
        filter_bar.append(lbl_idea)

        self._idea_model = Gtk.StringList.new(["Todos los proyectos"])
        self.filter_idea = Gtk.DropDown(model=self._idea_model, selected=0)
        self.filter_idea.connect("notify::selected", lambda *_: self._apply_filters())
        filter_bar.append(self.filter_idea)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        filter_bar.append(spacer)

        lbl_sort = Gtk.Label(label="Ordenar:")
        lbl_sort.add_css_class("dim-label")
        filter_bar.append(lbl_sort)

        sort_items = ["Fecha (reciente)", "Fecha (antigua)", "Nombre A-Z", "Estatus"]
        self.sort_combo = Gtk.DropDown(
            model=Gtk.StringList.new(sort_items), selected=0
        )
        self.sort_combo.connect("notify::selected", lambda *_: self._apply_filters())
        filter_bar.append(self.sort_combo)

        self.append(filter_bar)

        # ── Scrollable list ───────────────────────────────────────────────
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._content_stack = Gtk.Stack()
        self._content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        scroll.set_child(self._content_stack)

        self._status_page = Adw.StatusPage(
            icon_name="emblem-ok-symbolic",
            title="Sin tareas registradas",
            description='Haz clic en "Nueva tarea" para comenzar.',
        )
        self._content_stack.add_named(self._status_page, "empty")

        list_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        list_outer.set_margin_start(12)
        list_outer.set_margin_end(12)
        list_outer.set_margin_top(12)
        list_outer.set_margin_bottom(12)

        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("boxed-list")
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        list_outer.append(self.list_box)
        self._content_stack.add_named(list_outer, "list")

        self.append(scroll)

        # ── Count label ───────────────────────────────────────────────────
        self._count_label = Gtk.Label()
        self._count_label.add_css_class("dim-label")
        self._count_label.add_css_class("caption")
        self._count_label.add_css_class("count-label")
        self._count_label.set_halign(Gtk.Align.START)
        self.append(self._count_label)

        key_ctrl = Gtk.EventControllerKey()
        self.add_controller(key_ctrl)
        key_ctrl.connect("key-pressed", self._on_key_pressed)

    def _on_key_pressed(self, ctrl, keyval, keycode, state):
        from gi.repository import Gdk
        if keyval == Gdk.KEY_f and (state & Gdk.ModifierType.CONTROL_MASK):
            self.btn_search.set_active(not self.btn_search.get_active())
            return True
        return False

    # ── Public API ──────────────────────────────────────────────────────────

    def refresh(self):
        self._all_tareas = load_all_tareas()
        self._rebuild_idea_filter()
        self._apply_filters()

    def open_new_form(self):
        from .tarea_form import TareaFormWindow
        form = TareaFormWindow(parent=self.get_root())
        form.connect("tarea-saved", lambda _: self.refresh())
        form.present()

    # ── Private ─────────────────────────────────────────────────────────────

    def _rebuild_idea_filter(self):
        idx = self.filter_idea.get_selected()
        old_id = self._idea_ids[idx] if idx < len(self._idea_ids) else None

        ideas_en_tareas = sorted(
            set(
                (t.idea_id, t.idea_nombre)
                for t in self._all_tareas
            ),
            key=lambda x: x[1].lower(),
        )

        self._idea_ids = [None] + [iid for iid, _ in ideas_en_tareas]
        new_items = ["Todos los proyectos"] + [nombre for _, nombre in ideas_en_tareas]

        while self._idea_model.get_n_items() > 0:
            self._idea_model.remove(0)
        for item in new_items:
            self._idea_model.append(item)

        new_idx = 0
        for i, iid in enumerate(self._idea_ids):
            if iid == old_id:
                new_idx = i
                break
        self.filter_idea.set_selected(new_idx)

    def _apply_filters(self):
        tareas = list(self._all_tareas)

        search = self.search_entry.get_text().strip().lower()
        if search:
            tareas = [t for t in tareas if search in t.nombre.lower()]

        est_idx = self.filter_est.get_selected()
        if est_idx > 0:
            estatus = TAREA_STATUS_LIST[est_idx - 1]
            tareas = [t for t in tareas if t.estatus == estatus]

        idea_idx = self.filter_idea.get_selected()
        idea_id = self._idea_ids[idea_idx] if idea_idx < len(self._idea_ids) else None
        if idea_id:
            tareas = [t for t in tareas if t.idea_id == idea_id]

        STATUS_ORDER = {s: i for i, s in enumerate(TAREA_STATUS_LIST)}
        sort_idx = self.sort_combo.get_selected()
        if sort_idx == 0:
            tareas.sort(key=lambda t: t.fecha_creacion, reverse=True)
        elif sort_idx == 1:
            tareas.sort(key=lambda t: t.fecha_creacion)
        elif sort_idx == 2:
            tareas.sort(key=lambda t: t.nombre.lower())
        elif sort_idx == 3:
            tareas.sort(key=lambda t: STATUS_ORDER.get(t.estatus, 9))

        self._populate_list(tareas)
        count, total = len(tareas), len(self._all_tareas)
        suffix = f" (de {total} total)" if count != total else ""
        self._count_label.set_label(f"  {count} tarea{'s' if count != 1 else ''}{suffix}")

    def _populate_list(self, tareas: List[Tarea]):
        while True:
            row = self.list_box.get_first_child()
            if row is None:
                break
            self.list_box.remove(row)

        if not tareas:
            self._content_stack.set_visible_child_name("empty")
            return

        self._content_stack.set_visible_child_name("list")
        for tarea in tareas:
            self.list_box.append(self._make_row(tarea))

    def _make_row(self, tarea: Tarea) -> Adw.ActionRow:
        row = Adw.ActionRow()
        row.set_title(tarea.nombre)
        row.set_subtitle(f"{tarea.idea_nombre}  ·  {tarea.fecha_creacion_display()}")
        row.set_activatable(True)
        row.connect("activated", lambda _r: self._open_edit_form(tarea.id))

        dot = Gtk.Label(label="●")
        dot.add_css_class(STATUS_DOT.get(tarea.estatus, "dot-gray"))
        dot.set_valign(Gtk.Align.CENTER)
        row.add_prefix(dot)

        badge = Gtk.Label(label=tarea.estatus)
        badge.add_css_class("status-badge")
        badge.add_css_class(STATUS_BADGE.get(tarea.estatus, "badge-gray"))
        badge.set_valign(Gtk.Align.CENTER)
        row.add_suffix(badge)

        btn_edit = Gtk.Button(icon_name="document-edit-symbolic")
        btn_edit.add_css_class("flat")
        btn_edit.set_tooltip_text("Editar tarea")
        btn_edit.set_valign(Gtk.Align.CENTER)
        btn_edit.connect("clicked", lambda _b: self._open_edit_form(tarea.id))
        row.add_suffix(btn_edit)

        btn_del = Gtk.Button(icon_name="edit-delete-symbolic")
        btn_del.add_css_class("flat")
        btn_del.add_css_class("destructive-action")
        btn_del.set_tooltip_text("Eliminar tarea")
        btn_del.set_valign(Gtk.Align.CENTER)
        btn_del.connect("clicked", lambda _b: self._delete_tarea(tarea))
        row.add_suffix(btn_del)

        return row

    def _open_edit_form(self, tarea_id: str):
        from ..data_manager import load_tarea
        from .tarea_form import TareaFormWindow
        tarea = load_tarea(tarea_id)
        if tarea is None:
            self._toast_overlay.add_toast(
                Adw.Toast(title="No se encontró la tarea.")
            )
            return
        form = TareaFormWindow(tarea=tarea, parent=self.get_root())
        form.connect("tarea-saved", lambda _: self.refresh())
        form.present()

    def _delete_tarea(self, tarea: Tarea):
        if self._pending_delete is not None:
            self._pending_delete = None

        self._pending_delete = tarea
        delete_tarea(tarea.id)
        self.refresh()

        toast = Adw.Toast(title=f"Tarea «{tarea.nombre}» eliminada")
        toast.set_button_label("Deshacer")
        toast.set_timeout(5)
        toast.connect("button-clicked", self._undo_delete)
        toast.connect("dismissed", lambda _: setattr(self, "_pending_delete", None))
        self._toast_overlay.add_toast(toast)

    def _undo_delete(self, _toast):
        if self._pending_delete is not None:
            save_tarea(self._pending_delete)
            self._pending_delete = None
            self.refresh()
