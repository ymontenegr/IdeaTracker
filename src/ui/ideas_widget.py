from datetime import datetime
from typing import List, Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject

from ..data_manager import load_all_ideas, load_categories, delete_idea, save_idea
from ..models import Idea
from ..config import STATUS_LIST, PRIORIDADES


# ── Status → badge CSS class mapping ─────────────────────────────────────────
STATUS_BADGE = {
    "Por iniciar": "badge-blue",
    "Iniciado":    "badge-yellow",
    "En proceso":  "badge-orange",
    "Finalizado":  "badge-green",
    "Postergado":  "badge-gray",
    "Cancelado":   "badge-red",
}
STATUS_DOT = {
    "Por iniciar": "dot-blue",
    "Iniciado":    "dot-yellow",
    "En proceso":  "dot-orange",
    "Finalizado":  "dot-green",
    "Postergado":  "dot-gray",
    "Cancelado":   "dot-red",
}
PRIORIDAD_DOT = {
    "Alta":  "dot-red",
    "Media": "dot-orange",
    "Baja":  "dot-green",
}


class IdeasWidget(Gtk.Box):
    def __init__(self, toast_overlay: Adw.ToastOverlay):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._toast_overlay = toast_overlay
        self._all_ideas: List[Idea] = []
        self._pending_delete: Optional[Idea] = None   # for undo

        # Category ID list parallel to filter dropdown items
        self._cat_ids: List[Optional[str]] = [None]  # index 0 = "Todas"

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

        # Search toggle button
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

        # Category filter
        lbl_cat = Gtk.Label(label="Categoría:")
        lbl_cat.add_css_class("dim-label")
        filter_bar.append(lbl_cat)

        self._cat_model = Gtk.StringList.new(["Todas"])
        self.filter_cat = Gtk.DropDown(model=self._cat_model, selected=0)
        self.filter_cat.set_tooltip_text("Filtrar por categoría")
        self.filter_cat.connect("notify::selected", lambda *_: self._apply_filters())
        filter_bar.append(self.filter_cat)

        # Priority filter
        lbl_prio = Gtk.Label(label="Prioridad:")
        lbl_prio.add_css_class("dim-label")
        lbl_prio.set_margin_start(6)
        filter_bar.append(lbl_prio)

        prio_items = ["Todas"] + PRIORIDADES
        self.filter_prio = Gtk.DropDown(
            model=Gtk.StringList.new(prio_items), selected=0
        )
        self.filter_prio.set_tooltip_text("Filtrar por prioridad")
        self.filter_prio.connect("notify::selected", lambda *_: self._apply_filters())
        filter_bar.append(self.filter_prio)

        # Status filter
        lbl_est = Gtk.Label(label="Estatus:")
        lbl_est.add_css_class("dim-label")
        lbl_est.set_margin_start(6)
        filter_bar.append(lbl_est)

        status_items = ["Todos"] + STATUS_LIST
        self.filter_est = Gtk.DropDown(
            model=Gtk.StringList.new(status_items), selected=0
        )
        self.filter_est.set_tooltip_text("Filtrar por estatus")
        self.filter_est.connect("notify::selected", lambda *_: self._apply_filters())
        filter_bar.append(self.filter_est)

        # Month filter
        lbl_mes = Gtk.Label(label="Mes:")
        lbl_mes.add_css_class("dim-label")
        lbl_mes.set_margin_start(6)
        filter_bar.append(lbl_mes)

        self._mes_data: List[Optional[tuple]] = [None]
        self._mes_model = Gtk.StringList.new(["Todos los meses"])
        self.filter_mes = Gtk.DropDown(model=self._mes_model, selected=0)
        self.filter_mes.set_tooltip_text("Filtrar por mes de registro")
        self.filter_mes.connect("notify::selected", lambda *_: self._apply_filters())
        filter_bar.append(self.filter_mes)

        # Sort
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        filter_bar.append(spacer)

        lbl_sort = Gtk.Label(label="Ordenar:")
        lbl_sort.add_css_class("dim-label")
        filter_bar.append(lbl_sort)

        sort_items = [
            "Fecha (reciente)", "Fecha (antigua)", "Prioridad", "Nombre A-Z"
        ]
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

        # Stack: list vs. empty state
        self._content_stack = Gtk.Stack()
        self._content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        scroll.set_child(self._content_stack)

        # Empty state
        self._status_page = Adw.StatusPage(
            icon_name="document-edit-symbolic",
            title="Sin ideas registradas",
            description='Haz clic en "Nueva idea" para comenzar.',
        )
        self._content_stack.add_named(self._status_page, "empty")

        # List container
        list_box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        list_box_outer.set_margin_start(12)
        list_box_outer.set_margin_end(12)
        list_box_outer.set_margin_top(12)
        list_box_outer.set_margin_bottom(12)

        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("boxed-list")
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        list_box_outer.append(self.list_box)
        self._content_stack.add_named(list_box_outer, "list")

        self.append(scroll)

        # ── Count label ───────────────────────────────────────────────────
        self._count_label = Gtk.Label()
        self._count_label.add_css_class("dim-label")
        self._count_label.add_css_class("caption")
        self._count_label.add_css_class("count-label")
        self._count_label.set_halign(Gtk.Align.START)
        self.append(self._count_label)

        # Keyboard shortcut: Ctrl+F → toggle search
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
        self._all_ideas = load_all_ideas()
        self._rebuild_month_filter()
        self.refresh_categories()

    def refresh_categories(self):
        idx = self.filter_cat.get_selected()
        old_cat_id = self._cat_ids[idx] if idx < len(self._cat_ids) else None

        cats = load_categories()
        self._cat_ids = [None] + [c.id for c in cats]
        new_items = ["Todas"] + [c.nombre for c in cats]

        while self._cat_model.get_n_items() > 0:
            self._cat_model.remove(0)
        for item in new_items:
            self._cat_model.append(item)

        # Restore selection
        new_idx = 0
        for i, cid in enumerate(self._cat_ids):
            if cid == old_cat_id:
                new_idx = i
                break
        self.filter_cat.set_selected(new_idx)
        self._apply_filters()

    def open_new_form(self):
        from .idea_form import IdeaFormWindow
        form = IdeaFormWindow(parent=self.get_root())
        form.connect("idea-saved", lambda _: self.refresh())
        form.present()

    # ── Private ─────────────────────────────────────────────────────────────

    def _rebuild_month_filter(self):
        idx = self.filter_mes.get_selected()
        old_mes = self._mes_data[idx] if idx < len(self._mes_data) else None

        months = sorted(
            set(i.mes_registro() for i in self._all_ideas), reverse=True
        )
        months = [(y, m) for y, m in months if y != 0]

        self._mes_data = [None] + months
        new_items = ["Todos los meses"]
        for y, m in months:
            new_items.append(datetime(y, m, 1).strftime("%B %Y").capitalize())

        while self._mes_model.get_n_items() > 0:
            self._mes_model.remove(0)
        for item in new_items:
            self._mes_model.append(item)

        new_idx = 0
        for i, mes in enumerate(self._mes_data):
            if mes == old_mes:
                new_idx = i
                break
        self.filter_mes.set_selected(new_idx)

    def _apply_filters(self):
        ideas = list(self._all_ideas)

        # Search
        search = self.search_entry.get_text().strip().lower()
        if search:
            ideas = [i for i in ideas if search in i.nombre.lower()]

        # Category
        cat_idx = self.filter_cat.get_selected()
        cat_id = self._cat_ids[cat_idx] if cat_idx < len(self._cat_ids) else None
        if cat_id:
            ideas = [i for i in ideas if i.categoria_id == cat_id]

        # Priority
        prio_idx = self.filter_prio.get_selected()
        if prio_idx > 0:
            prioridad = PRIORIDADES[prio_idx - 1]
            ideas = [i for i in ideas if i.prioridad == prioridad]

        # Status
        est_idx = self.filter_est.get_selected()
        if est_idx > 0:
            estatus = STATUS_LIST[est_idx - 1]
            ideas = [i for i in ideas if i.estatus == estatus]

        # Month
        mes_idx = self.filter_mes.get_selected()
        mes = self._mes_data[mes_idx] if mes_idx < len(self._mes_data) else None
        if mes:
            ideas = [i for i in ideas if i.mes_registro() == mes]

        # Sort
        PRIO_ORDER = {"Alta": 0, "Media": 1, "Baja": 2}
        sort_idx = self.sort_combo.get_selected()
        if sort_idx == 0:
            ideas.sort(key=lambda i: i.fecha_registro, reverse=True)
        elif sort_idx == 1:
            ideas.sort(key=lambda i: i.fecha_registro)
        elif sort_idx == 2:
            ideas.sort(key=lambda i: PRIO_ORDER.get(i.prioridad, 9))
        elif sort_idx == 3:
            ideas.sort(key=lambda i: i.nombre.lower())

        self._populate_list(ideas)
        count, total = len(ideas), len(self._all_ideas)
        suffix = f" (de {total} total)" if count != total else ""
        self._count_label.set_label(f"  {count} idea{'s' if count != 1 else ''}{suffix}")

    def _populate_list(self, ideas: List[Idea]):
        # Remove all existing rows
        while True:
            row = self.list_box.get_first_child()
            if row is None:
                break
            self.list_box.remove(row)

        if not ideas:
            self._content_stack.set_visible_child_name("empty")
            return

        self._content_stack.set_visible_child_name("list")
        for idea in ideas:
            row = self._make_row(idea)
            self.list_box.append(row)

    def _make_row(self, idea: Idea) -> Adw.ActionRow:
        row = Adw.ActionRow()
        row.set_title(idea.nombre)
        row.set_subtitle(
            f"{idea.categoria_nombre}  ·  {idea.fecha_registro_display()}"
        )
        row.set_activatable(True)
        row.connect("activated", lambda _r: self._open_edit_form(idea.id))

        # Prefix: status color dot
        dot = Gtk.Label(label="●")
        dot_class = STATUS_DOT.get(idea.estatus, "dot-gray")
        dot.add_css_class(dot_class)
        dot.set_valign(Gtk.Align.CENTER)
        row.add_prefix(dot)

        # Suffix: priority badge + status badge + edit + delete
        prio_badge = Gtk.Label(label=idea.prioridad)
        prio_badge.add_css_class("status-badge")
        prio_badge.add_css_class(PRIORIDAD_DOT.get(idea.prioridad, "dot-gray").replace("dot-", "badge-"))
        prio_badge.set_valign(Gtk.Align.CENTER)
        row.add_suffix(prio_badge)

        status_badge = Gtk.Label(label=idea.estatus)
        status_badge.add_css_class("status-badge")
        status_badge.add_css_class(STATUS_BADGE.get(idea.estatus, "badge-gray"))
        status_badge.set_valign(Gtk.Align.CENTER)
        row.add_suffix(status_badge)

        btn_edit = Gtk.Button(icon_name="document-edit-symbolic")
        btn_edit.add_css_class("flat")
        btn_edit.set_tooltip_text("Editar idea")
        btn_edit.set_valign(Gtk.Align.CENTER)
        btn_edit.connect("clicked", lambda _b: self._open_edit_form(idea.id))
        row.add_suffix(btn_edit)

        btn_del = Gtk.Button(icon_name="edit-delete-symbolic")
        btn_del.add_css_class("flat")
        btn_del.add_css_class("destructive-action")
        btn_del.set_tooltip_text("Eliminar idea")
        btn_del.set_valign(Gtk.Align.CENTER)
        btn_del.connect("clicked", lambda _b: self._delete_idea(idea))
        row.add_suffix(btn_del)

        return row

    def _open_edit_form(self, idea_id: str):
        from ..data_manager import load_idea
        from .idea_form import IdeaFormWindow
        idea = load_idea(idea_id)
        if idea is None:
            self._show_error("No se encontró la idea.")
            return
        form = IdeaFormWindow(idea=idea, parent=self.get_root())
        form.connect("idea-saved", lambda _: self.refresh())
        form.present()

    def _delete_idea(self, idea: Idea):
        """Delete immediately, offer undo via toast."""
        # Cancel any previous pending delete
        if self._pending_delete is not None:
            self._flush_pending_delete()

        self._pending_delete = idea
        delete_idea(idea.id)
        self.refresh()

        toast = Adw.Toast(title=f"Idea «{idea.nombre}» eliminada")
        toast.set_button_label("Deshacer")
        toast.set_timeout(5)
        toast.connect("button-clicked", self._undo_delete)
        toast.connect("dismissed", self._on_toast_dismissed)
        self._toast_overlay.add_toast(toast)

    def _undo_delete(self, _toast):
        if self._pending_delete is not None:
            save_idea(self._pending_delete)
            self._pending_delete = None
            self.refresh()

    def _on_toast_dismissed(self, _toast):
        self._pending_delete = None

    def _flush_pending_delete(self):
        """Commit a pending delete (toast timed out) — data already deleted."""
        self._pending_delete = None

    def _show_error(self, message: str):
        toast = Adw.Toast(title=message)
        toast.set_timeout(3)
        self._toast_overlay.add_toast(toast)
