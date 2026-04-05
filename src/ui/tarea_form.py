from typing import Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject

from ..data_manager import (
    load_all_ideas, create_tarea, save_tarea,
    cambiar_estatus_tarea, load_tarea, add_nota_tarea,
)
from ..models import Tarea
from ..config import TAREA_STATUS_LIST, IDEA_DEFAULT_ID, IDEA_DEFAULT_NAME


class TareaFormWindow(Adw.Window):
    """Secondary window for creating / editing a task."""

    __gsignals__ = {
        "tarea-saved": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(
        self,
        tarea: Optional[Tarea] = None,
        idea_id: Optional[str] = None,
        idea_nombre: Optional[str] = None,
        parent=None,
    ):
        super().__init__(transient_for=parent, modal=True)
        self._tarea = tarea
        self._is_edit = tarea is not None
        self._preset_idea_id = idea_id
        self._preset_idea_nombre = idea_nombre
        self.set_title("Editar tarea" if self._is_edit else "Nueva tarea")
        self.set_default_size(640, 560)
        self.set_size_request(480, 420)
        self._build_ui()
        if self._is_edit:
            self._populate_fields()
        elif self._preset_idea_id:
            self._select_preset_idea()

    # ── Build UI ────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._toast_overlay = Adw.ToastOverlay()
        self.set_content(self._toast_overlay)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._toast_overlay.set_child(main_box)

        # Header bar
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)

        btn_cancel = Gtk.Button(label="Cancelar")
        btn_cancel.add_css_class("flat")
        btn_cancel.connect("clicked", lambda _: self.close())
        header.pack_start(btn_cancel)

        self.btn_save = Gtk.Button(label="Guardar")
        self.btn_save.add_css_class("suggested-action")
        self.btn_save.connect("clicked", self._on_save)
        header.pack_end(self.btn_save)

        main_box.append(header)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        clamp = Adw.Clamp()
        clamp.set_maximum_size(620)
        clamp.set_margin_start(12)
        clamp.set_margin_end(12)
        clamp.set_margin_top(12)
        clamp.set_margin_bottom(24)

        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        clamp.set_child(form_box)
        scroll.set_child(clamp)
        main_box.append(scroll)

        # ── Section 1: Información ────────────────────────────────────────
        grp_info = Adw.PreferencesGroup(title="Información de la tarea")

        self.nombre_row = Adw.EntryRow(title="Nombre *")
        grp_info.add(self.nombre_row)

        form_box.append(grp_info)

        # Description (multi-line)
        grp_desc = Adw.PreferencesGroup(title="Descripción")
        self.desc_view = Gtk.TextView()
        self.desc_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.desc_view.add_css_class("view")
        self.desc_view.set_margin_start(12)
        self.desc_view.set_margin_end(12)
        self.desc_view.set_margin_top(10)
        self.desc_view.set_margin_bottom(10)
        scroll_desc = Gtk.ScrolledWindow()
        scroll_desc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_desc.set_min_content_height(80)
        scroll_desc.set_child(self.desc_view)
        desc_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        desc_card.add_css_class("card")
        desc_card.append(scroll_desc)
        grp_desc.add(desc_card)
        form_box.append(grp_desc)

        # ── Section 2: Proyecto asociado ─────────────────────────────────
        grp_proyecto = Adw.PreferencesGroup(title="Proyecto asociado")

        self.idea_row = Adw.ComboRow(title="Proyecto / Idea")
        ideas = sorted(load_all_ideas(), key=lambda i: i.nombre.lower())
        self._idea_ids = [IDEA_DEFAULT_ID] + [i.id for i in ideas]
        idea_nombres = [IDEA_DEFAULT_NAME] + [i.nombre for i in ideas]
        self.idea_row.set_model(Gtk.StringList.new(idea_nombres))
        self.idea_row.set_selected(0)
        grp_proyecto.add(self.idea_row)

        if self._is_edit and self._tarea:
            date_row = Adw.ActionRow(title="Fecha de creación")
            lbl = Gtk.Label(label=self._tarea.fecha_creacion_display())
            lbl.add_css_class("dim-label")
            lbl.set_valign(Gtk.Align.CENTER)
            date_row.add_suffix(lbl)
            grp_proyecto.add(date_row)

        form_box.append(grp_proyecto)

        # ── Section 3: Estatus (edit only) ────────────────────────────────
        if self._is_edit:
            grp_status = Adw.PreferencesGroup(title="Estatus")

            self.estatus_row = Adw.ComboRow(title="Estatus actual")
            self.estatus_row.set_model(Gtk.StringList.new(TAREA_STATUS_LIST))
            self.estatus_row.set_selected(0)
            grp_status.add(self.estatus_row)

            form_box.append(grp_status)

            # ── Historial ─────────────────────────────────────────────────
            self._grp_historial = Adw.PreferencesGroup(title="Historial de estatus")
            self._historial_box = Gtk.ListBox()
            self._historial_box.add_css_class("boxed-list")
            self._historial_box.set_selection_mode(Gtk.SelectionMode.NONE)
            self._grp_historial.add(self._historial_box)
            form_box.append(self._grp_historial)

            # ── Notas ─────────────────────────────────────────────────────
            self._grp_notas = Adw.PreferencesGroup(title="Notas / observaciones")
            self._notas_box = Gtk.ListBox()
            self._notas_box.add_css_class("boxed-list")
            self._notas_box.set_selection_mode(Gtk.SelectionMode.NONE)
            self._grp_notas.add(self._notas_box)

            self.nota_row = Adw.EntryRow(title="Nueva nota…")
            btn_add = Gtk.Button(icon_name="list-add-symbolic")
            btn_add.add_css_class("flat")
            btn_add.set_tooltip_text("Agregar nota")
            btn_add.set_valign(Gtk.Align.CENTER)
            btn_add.connect("clicked", self._on_add_nota)
            self.nota_row.add_suffix(btn_add)
            self.nota_row.connect("entry-activated", self._on_add_nota)
            self._grp_notas.add(self.nota_row)
            form_box.append(self._grp_notas)

    # ── Populate ────────────────────────────────────────────────────────────

    def _populate_fields(self):
        t = self._tarea
        self.nombre_row.set_text(t.nombre)
        buf = self.desc_view.get_buffer()
        buf.set_text(t.descripcion)

        try:
            idx = self._idea_ids.index(t.idea_id)
            self.idea_row.set_selected(idx)
        except ValueError:
            pass

        try:
            est_idx = TAREA_STATUS_LIST.index(t.estatus)
            self.estatus_row.set_selected(est_idx)
        except ValueError:
            pass

        self._populate_historial()
        self._populate_notas()

    def _select_preset_idea(self):
        if self._preset_idea_id:
            try:
                idx = self._idea_ids.index(self._preset_idea_id)
                self.idea_row.set_selected(idx)
            except ValueError:
                pass

    def _populate_historial(self):
        while True:
            child = self._historial_box.get_first_child()
            if child is None:
                break
            self._historial_box.remove(child)

        if not self._tarea or not self._tarea.historial_estatus:
            self._historial_box.append(
                Adw.ActionRow(title="Sin historial registrado")
            )
            return

        for h in reversed(self._tarea.historial_estatus):
            row = Adw.ActionRow(
                title=h.estatus,
                subtitle=h.fecha_display(),
            )
            self._historial_box.append(row)

    def _populate_notas(self):
        while True:
            child = self._notas_box.get_first_child()
            if child is None:
                break
            self._notas_box.remove(child)

        if not self._tarea or not self._tarea.notas:
            self._notas_box.append(
                Adw.ActionRow(title="Sin notas registradas")
            )
            return

        for nota in reversed(self._tarea.notas):
            row = Adw.ActionRow(
                title=nota.texto,
                subtitle=nota.fecha_display(),
            )
            self._notas_box.append(row)

    # ── Actions ─────────────────────────────────────────────────────────────

    def _on_add_nota(self, *_):
        if not self._tarea:
            return
        texto = self.nota_row.get_text().strip()
        if not texto:
            self._show_toast("Escribe el texto de la nota.")
            return
        updated = add_nota_tarea(self._tarea.id, texto)
        if updated:
            self._tarea = updated
            self.nota_row.set_text("")
            self._populate_notas()

    def _on_save(self, _button):
        nombre = self.nombre_row.get_text().strip()
        if not nombre:
            self.nombre_row.add_css_class("error")
            self._show_toast("El nombre de la tarea es obligatorio.")
            return
        self.nombre_row.remove_css_class("error")

        buf = self.desc_view.get_buffer()
        descripcion = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False).strip()

        idea_idx = self.idea_row.get_selected()
        idea_id = self._idea_ids[idea_idx] if idea_idx < len(self._idea_ids) else IDEA_DEFAULT_ID
        idea_model = self.idea_row.get_model()
        idea_nombre = idea_model.get_string(idea_idx) if idea_model else IDEA_DEFAULT_NAME

        if self._is_edit and self._tarea:
            self._tarea.nombre = nombre
            self._tarea.descripcion = descripcion
            self._tarea.idea_id = idea_id
            self._tarea.idea_nombre = idea_nombre

            nuevo_estatus = TAREA_STATUS_LIST[self.estatus_row.get_selected()]
            if nuevo_estatus != self._tarea.estatus:
                cambiar_estatus_tarea(self._tarea.id, nuevo_estatus)
                updated = load_tarea(self._tarea.id)
                if updated:
                    updated.nombre = nombre
                    updated.descripcion = descripcion
                    updated.idea_id = idea_id
                    updated.idea_nombre = idea_nombre
                    save_tarea(updated)
            else:
                save_tarea(self._tarea)
        else:
            create_tarea(
                nombre=nombre,
                descripcion=descripcion,
                idea_id=idea_id,
                idea_nombre=idea_nombre,
            )

        self.emit("tarea-saved")
        self.close()

    def _show_toast(self, message: str):
        toast = Adw.Toast(title=message)
        toast.set_timeout(4)
        self._toast_overlay.add_toast(toast)
