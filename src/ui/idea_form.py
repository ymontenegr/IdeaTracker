from datetime import datetime, date
from typing import Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject

from ..data_manager import load_categories, create_idea, save_idea, add_nota
from ..models import Idea
from ..config import STATUS_LIST, PRIORIDADES, ORIGENES_DEFAULT


class IdeaFormWindow(Adw.Window):
    """Secondary window for creating / editing an idea."""

    __gsignals__ = {
        "idea-saved": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, idea: Optional[Idea] = None, parent=None):
        super().__init__(transient_for=parent, modal=True)
        self._idea = idea
        self._is_edit = idea is not None
        self.set_title("Editar idea" if self._is_edit else "Nueva idea")
        self.set_default_size(720, 680)
        self.set_size_request(540, 500)
        self._build_ui()
        if self._is_edit:
            self._populate_fields()

    # ── Build UI ────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Toast overlay for inline validation messages
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

        # Scrollable form body
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        clamp = Adw.Clamp()
        clamp.set_maximum_size(700)
        clamp.set_margin_start(12)
        clamp.set_margin_end(12)
        clamp.set_margin_top(12)
        clamp.set_margin_bottom(24)

        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        clamp.set_child(form_box)
        scroll.set_child(clamp)
        main_box.append(scroll)

        # ── Section 1: Información general ───────────────────────────────
        grp_info = Adw.PreferencesGroup(title="Información general")

        self.nombre_row = Adw.EntryRow(title="Nombre / tema *")
        grp_info.add(self.nombre_row)

        self.origen_row = Adw.ComboRow(title="Origen de la idea *")
        origen_model = Gtk.StringList.new(ORIGENES_DEFAULT)
        self.origen_row.set_model(origen_model)
        self.origen_row.set_selected(0)
        grp_info.add(self.origen_row)

        form_box.append(grp_info)

        # Description (multi-line — external card)
        grp_desc = Adw.PreferencesGroup(title="Descripción *")
        self.desc_view = Gtk.TextView()
        self.desc_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.desc_view.add_css_class("view")
        self.desc_view.set_margin_start(12)
        self.desc_view.set_margin_end(12)
        self.desc_view.set_margin_top(10)
        self.desc_view.set_margin_bottom(10)
        scroll_desc = Gtk.ScrolledWindow()
        scroll_desc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_desc.set_min_content_height(90)
        scroll_desc.set_child(self.desc_view)
        desc_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        desc_card.add_css_class("card")
        desc_card.append(scroll_desc)
        grp_desc.add(desc_card)
        form_box.append(grp_desc)

        # ── Section 2: Fechas y costos ────────────────────────────────────
        grp_fechas = Adw.PreferencesGroup(title="Fechas y costos")

        # Fecha de registro (read-only display)
        reg_row = Adw.ActionRow(title="Fecha de registro")
        if self._is_edit and self._idea:
            try:
                dt = datetime.fromisoformat(self._idea.fecha_registro)
                reg_label = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                reg_label = self._idea.fecha_registro
        else:
            reg_label = datetime.now().strftime("%d/%m/%Y %H:%M") + "  (automática)"
        reg_lbl = Gtk.Label(label=reg_label)
        reg_lbl.add_css_class("dim-label")
        reg_lbl.set_valign(Gtk.Align.CENTER)
        reg_row.add_suffix(reg_lbl)
        grp_fechas.add(reg_row)

        self.fecha_inicio_row = Adw.EntryRow(title="Fecha probable de inicio *")
        self.fecha_inicio_row.set_text(date.today().strftime("%d/%m/%Y"))
        self.fecha_inicio_row.set_input_hints(Gtk.InputHints.NO_SPELLCHECK)
        grp_fechas.add(self.fecha_inicio_row)

        self.costo_row = Adw.SpinRow.new_with_range(0, 999_999_999, 100)
        self.costo_row.set_title("Costo aproximado ($) *")
        self.costo_row.set_digits(2)
        grp_fechas.add(self.costo_row)

        form_box.append(grp_fechas)

        # Beneficio esperado (multi-line)
        grp_beneficio = Adw.PreferencesGroup(title="Beneficio esperado *")
        self.beneficio_view = Gtk.TextView()
        self.beneficio_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.beneficio_view.add_css_class("view")
        self.beneficio_view.set_margin_start(12)
        self.beneficio_view.set_margin_end(12)
        self.beneficio_view.set_margin_top(10)
        self.beneficio_view.set_margin_bottom(10)
        scroll_ben = Gtk.ScrolledWindow()
        scroll_ben.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_ben.set_min_content_height(70)
        scroll_ben.set_child(self.beneficio_view)
        ben_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        ben_card.add_css_class("card")
        ben_card.append(scroll_ben)
        grp_beneficio.add(ben_card)
        form_box.append(grp_beneficio)

        # ── Section 3: Clasificación ──────────────────────────────────────
        grp_class = Adw.PreferencesGroup(title="Clasificación")

        self.cat_row = Adw.ComboRow(title="Categoría *")
        cats = load_categories()
        self._cat_ids = [c.id for c in cats]
        cat_names = [c.nombre for c in cats]
        if not cat_names:
            cat_names = ["(Sin categorías — crea una en Configuración)"]
        self.cat_row.set_model(Gtk.StringList.new(cat_names))
        self.cat_row.set_selected(0)
        grp_class.add(self.cat_row)

        self.prio_row = Adw.ComboRow(title="Prioridad *")
        self.prio_row.set_model(Gtk.StringList.new(PRIORIDADES))
        self.prio_row.set_selected(1)  # Media
        grp_class.add(self.prio_row)

        if self._is_edit:
            self.estatus_row = Adw.ComboRow(title="Estatus")
            self.estatus_row.set_model(Gtk.StringList.new(STATUS_LIST))
            self.estatus_row.set_selected(0)
            grp_class.add(self.estatus_row)

        form_box.append(grp_class)

        # ── Section 4: Notas (edit only) ─────────────────────────────────
        if self._is_edit:
            self._grp_notas = Adw.PreferencesGroup(title="Notas / observaciones")
            self._notas_box = Gtk.ListBox()
            self._notas_box.add_css_class("boxed-list")
            self._notas_box.set_selection_mode(Gtk.SelectionMode.NONE)
            self._grp_notas.add(self._notas_box)

            self.nota_row = Adw.EntryRow(title="Nueva nota…")
            btn_add_nota = Gtk.Button(icon_name="list-add-symbolic")
            btn_add_nota.add_css_class("flat")
            btn_add_nota.set_tooltip_text("Agregar nota")
            btn_add_nota.set_valign(Gtk.Align.CENTER)
            btn_add_nota.connect("clicked", self._on_add_nota)
            self.nota_row.add_suffix(btn_add_nota)
            self.nota_row.connect("entry-activated", self._on_add_nota)
            self._grp_notas.add(self.nota_row)
            form_box.append(self._grp_notas)

            # ── Section 5: Tareas (edit only) ─────────────────────────────
            self._grp_tareas = Adw.PreferencesGroup(title="Tareas")
            self._tareas_box = Gtk.ListBox()
            self._tareas_box.add_css_class("boxed-list")
            self._tareas_box.set_selection_mode(Gtk.SelectionMode.NONE)
            self._grp_tareas.add(self._tareas_box)

            self.tarea_row = Adw.EntryRow(title="Nombre de la nueva tarea…")
            btn_add_tarea = Gtk.Button(icon_name="list-add-symbolic")
            btn_add_tarea.add_css_class("flat")
            btn_add_tarea.set_tooltip_text("Agregar tarea")
            btn_add_tarea.set_valign(Gtk.Align.CENTER)
            btn_add_tarea.connect("clicked", self._on_add_tarea)
            self.tarea_row.add_suffix(btn_add_tarea)
            self.tarea_row.connect("entry-activated", self._on_add_tarea)
            self._grp_tareas.add(self.tarea_row)
            form_box.append(self._grp_tareas)

    # ── Populate (edit mode) ────────────────────────────────────────────────

    def _populate_fields(self):
        idea = self._idea
        self.nombre_row.set_text(idea.nombre)

        # Descripción
        self.desc_view.get_buffer().set_text(idea.descripcion)

        # Origen
        try:
            idx = ORIGENES_DEFAULT.index(idea.origen)
            self.origen_row.set_selected(idx)
        except ValueError:
            # Custom origin — add it temporarily
            model = self.origen_row.get_model()
            model.append(idea.origen)
            self.origen_row.set_selected(model.get_n_items() - 1)

        # Fecha inicio
        try:
            d = date.fromisoformat(idea.fecha_inicio_probable)
            self.fecha_inicio_row.set_text(d.strftime("%d/%m/%Y"))
        except Exception:
            self.fecha_inicio_row.set_text(idea.fecha_inicio_probable)

        self.costo_row.set_value(idea.costo_aproximado)
        self.beneficio_view.get_buffer().set_text(idea.beneficio_esperado)

        # Categoría
        try:
            cat_idx = self._cat_ids.index(idea.categoria_id)
            self.cat_row.set_selected(cat_idx)
        except (ValueError, AttributeError):
            pass

        # Prioridad
        try:
            prio_idx = PRIORIDADES.index(idea.prioridad)
            self.prio_row.set_selected(prio_idx)
        except ValueError:
            pass

        # Estatus
        if self._is_edit and hasattr(self, "estatus_row"):
            try:
                est_idx = STATUS_LIST.index(idea.estatus)
                self.estatus_row.set_selected(est_idx)
            except ValueError:
                pass

        self._populate_notas()
        self._populate_tareas()

    def _populate_notas(self):
        while True:
            child = self._notas_box.get_first_child()
            if child is None:
                break
            self._notas_box.remove(child)

        if not self._idea or not self._idea.notas:
            empty = Adw.ActionRow(title="Sin notas registradas")
            empty.add_css_class("dim-label")
            self._notas_box.append(empty)
            return

        for nota in reversed(self._idea.notas):
            row = Adw.ActionRow(
                title=nota.texto,
                subtitle=nota.fecha_display(),
            )
            self._notas_box.append(row)

    def _populate_tareas(self):
        while True:
            child = self._tareas_box.get_first_child()
            if child is None:
                break
            self._tareas_box.remove(child)

        from ..data_manager import load_tareas_by_idea
        from ..config import TAREA_STATUS_COLORS

        tareas = []
        if self._idea:
            tareas = load_tareas_by_idea(self._idea.id)

        if not tareas:
            empty = Adw.ActionRow(title="Sin tareas registradas")
            empty.add_css_class("dim-label")
            self._tareas_box.append(empty)
            return

        for t in sorted(tareas, key=lambda x: x.fecha_creacion, reverse=True):
            row = Adw.ActionRow(
                title=t.nombre,
                subtitle=f"[{t.estatus}]  ·  {t.fecha_creacion_display()}",
            )
            self._tareas_box.append(row)

    # ── Actions ─────────────────────────────────────────────────────────────

    def _on_add_nota(self, *_):
        if not self._idea:
            return
        text = self.nota_row.get_text().strip()
        if not text:
            self._show_toast("Escribe el texto de la nota.")
            return
        updated = add_nota(self._idea.id, text)
        if updated:
            self._idea = updated
            self.nota_row.set_text("")
            self._populate_notas()

    def _on_add_tarea(self, *_):
        from ..data_manager import create_tarea
        if not self._idea:
            return
        nombre = self.tarea_row.get_text().strip()
        if not nombre:
            self._show_toast("Escribe el nombre de la tarea.")
            return
        create_tarea(
            nombre=nombre,
            descripcion="",
            idea_id=self._idea.id,
            idea_nombre=self._idea.nombre,
        )
        self.tarea_row.set_text("")
        self._populate_tareas()

    def _on_save(self, _button):
        nombre = self.nombre_row.get_text().strip()
        buf_desc = self.desc_view.get_buffer()
        descripcion = buf_desc.get_text(buf_desc.get_start_iter(), buf_desc.get_end_iter(), False).strip()
        buf_ben = self.beneficio_view.get_buffer()
        beneficio = buf_ben.get_text(buf_ben.get_start_iter(), buf_ben.get_end_iter(), False).strip()
        origen_idx = self.origen_row.get_selected()
        origen_model = self.origen_row.get_model()
        origen = origen_model.get_string(origen_idx) if origen_model else ""

        # Validation
        errors = []
        if not nombre:
            errors.append("Nombre / tema es obligatorio.")
            self.nombre_row.add_css_class("error")
        else:
            self.nombre_row.remove_css_class("error")
        if not descripcion:
            errors.append("Descripción es obligatoria.")
        if not beneficio:
            errors.append("Beneficio esperado es obligatorio.")
        if not self._cat_ids:
            errors.append("Crea al menos una categoría en Configuración.")

        if errors:
            self._show_toast(" · ".join(errors))
            return

        # Fecha inicio
        fecha_str = self.fecha_inicio_row.get_text().strip()
        try:
            parts = fecha_str.split("/")
            fecha_inicio = f"{parts[2]}-{parts[1]}-{parts[0]}"
        except Exception:
            self._show_toast("Formato de fecha inválido. Usa DD/MM/AAAA.")
            return

        cat_idx = self.cat_row.get_selected()
        cat_id = self._cat_ids[cat_idx] if cat_idx < len(self._cat_ids) else ""
        cat_model = self.cat_row.get_model()
        cat_nombre = cat_model.get_string(cat_idx) if cat_model else ""

        prio_idx = self.prio_row.get_selected()
        prioridad = PRIORIDADES[prio_idx] if prio_idx < len(PRIORIDADES) else "Media"

        costo = self.costo_row.get_value()

        if self._is_edit and self._idea:
            self._idea.nombre = nombre
            self._idea.descripcion = descripcion
            self._idea.origen = origen
            self._idea.fecha_inicio_probable = fecha_inicio
            self._idea.costo_aproximado = costo
            self._idea.beneficio_esperado = beneficio
            self._idea.categoria_id = cat_id
            self._idea.categoria_nombre = cat_nombre
            self._idea.prioridad = prioridad
            if hasattr(self, "estatus_row"):
                est_idx = self.estatus_row.get_selected()
                self._idea.estatus = STATUS_LIST[est_idx] if est_idx < len(STATUS_LIST) else "Por iniciar"
            save_idea(self._idea)
        else:
            create_idea(
                nombre=nombre,
                descripcion=descripcion,
                origen=origen,
                fecha_inicio_probable=fecha_inicio,
                costo_aproximado=costo,
                beneficio_esperado=beneficio,
                categoria_id=cat_id,
                categoria_nombre=cat_nombre,
                prioridad=prioridad,
            )

        self.emit("idea-saved")
        self.close()

    def _show_toast(self, message: str):
        toast = Adw.Toast(title=message)
        toast.set_timeout(4)
        self._toast_overlay.add_toast(toast)
