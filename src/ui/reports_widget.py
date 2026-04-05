from datetime import datetime
from typing import List

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gio", "2.0")
gi.require_version("GLib", "2.0")

from gi.repository import Gtk, Adw, Gio, GLib

from ..data_manager import load_all_ideas, load_idea, load_all_tareas, load_tarea
from ..models import Idea


class ReportsWidget(Gtk.Box):
    def __init__(self, toast_overlay: Adw.ToastOverlay):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._toast_overlay = toast_overlay
        self._ideas: List[Idea] = []
        self._build_ui()
        self.refresh()

    # ── Build UI ────────────────────────────────────────────────────────────

    def _build_ui(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        clamp = Adw.Clamp()
        clamp.set_maximum_size(800)
        clamp.set_margin_start(12)
        clamp.set_margin_end(12)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        clamp.set_child(content)
        scroll.set_child(clamp)
        self.append(scroll)

        # ── Report 1: Idea detail ─────────────────────────────────────────
        grp1 = Adw.PreferencesGroup(
            title="Reporte detallado por idea",
            description=(
                "Muestra todos los campos de una idea, historial de notas "
                "y estatus actual."
            ),
        )

        self.idea_row = Adw.ComboRow(title="Seleccionar idea")
        self._idea_model = Gtk.StringList.new([])
        self.idea_row.set_model(self._idea_model)
        grp1.add(self.idea_row)

        btn_row1 = self._make_button_row(
            on_view=self._on_view_idea,
            on_pdf=self._on_pdf_idea,
        )
        grp1.add(btn_row1)
        content.append(grp1)

        # ── Report 2: Monthly ─────────────────────────────────────────────
        grp2 = Adw.PreferencesGroup(
            title="Reporte mensual de ideas",
            description=(
                "Resumen de todas las ideas registradas en un mes/año "
                "específico, con totales por estatus."
            ),
        )

        self.mes_row = Adw.ComboRow(title="Seleccionar mes")
        self._mes_model = Gtk.StringList.new([])
        self.mes_row.set_model(self._mes_model)
        grp2.add(self.mes_row)

        btn_row2 = self._make_button_row(
            on_view=self._on_view_monthly,
            on_pdf=self._on_pdf_monthly,
        )
        grp2.add(btn_row2)
        content.append(grp2)

        # ── Report 3: Task detail ─────────────────────────────────────────
        grp3 = Adw.PreferencesGroup(
            title="Reporte detallado de tarea",
            description=(
                "Muestra la descripción, estatus actual e historial completo "
                "de cambios de una tarea."
            ),
        )

        self.tarea_row = Adw.ComboRow(title="Seleccionar tarea")
        self._tarea_model = Gtk.StringList.new([])
        self.tarea_row.set_model(self._tarea_model)
        grp3.add(self.tarea_row)

        btn_row3 = self._make_button_row(
            on_view=self._on_view_task,
            on_pdf=self._on_pdf_task,
        )
        grp3.add(btn_row3)
        content.append(grp3)

    def _make_button_row(self, on_view, on_pdf) -> Gtk.Box:
        """Returns a row with [Ver reporte] [Generar PDF] buttons."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.set_halign(Gtk.Align.END)
        box.set_margin_top(4)
        box.set_margin_bottom(4)

        btn_view = Gtk.Button(label="Ver reporte")
        btn_view.add_css_class("suggested-action")
        btn_view.connect("clicked", lambda _: on_view())
        box.append(btn_view)

        btn_pdf = Gtk.Button(label="Generar PDF")
        btn_pdf.connect("clicked", lambda _: on_pdf())
        box.append(btn_pdf)

        return box

    # ── Public API ──────────────────────────────────────────────────────────

    def refresh(self):
        self._ideas = load_all_ideas()
        self._populate_idea_combo()
        self._populate_month_combo()
        self._populate_tarea_combo()

    # ── Populate combos ─────────────────────────────────────────────────────

    def _populate_idea_combo(self):
        while self._idea_model.get_n_items() > 0:
            self._idea_model.remove(0)
        self._idea_ids: List[str] = []

        ideas = sorted(self._ideas, key=lambda i: i.nombre.lower())
        if ideas:
            for idea in ideas:
                self._idea_model.append(idea.nombre)
                self._idea_ids.append(idea.id)
        else:
            self._idea_model.append("(Sin ideas registradas)")
            self._idea_ids.append("")
        self.idea_row.set_selected(0)

    def _populate_month_combo(self):
        while self._mes_model.get_n_items() > 0:
            self._mes_model.remove(0)
        self._mes_data: List = []

        months = sorted(
            set(i.mes_registro() for i in self._ideas), reverse=True
        )
        months = [(y, m) for y, m in months if y != 0]

        if months:
            for y, m in months:
                self._mes_model.append(
                    datetime(y, m, 1).strftime("%B %Y").capitalize()
                )
                self._mes_data.append((y, m))
        else:
            self._mes_model.append("(Sin datos)")
            self._mes_data.append(None)
        self.mes_row.set_selected(0)

    def _populate_tarea_combo(self):
        while self._tarea_model.get_n_items() > 0:
            self._tarea_model.remove(0)
        self._tarea_ids: List[str] = []

        tareas = sorted(load_all_tareas(), key=lambda t: t.nombre.lower())
        if tareas:
            for t in tareas:
                self._tarea_model.append(f"{t.nombre}  [{t.idea_nombre}]")
                self._tarea_ids.append(t.id)
        else:
            self._tarea_model.append("(Sin tareas registradas)")
            self._tarea_ids.append("")
        self.tarea_row.set_selected(0)

    # ── View handlers ────────────────────────────────────────────────────────

    def _on_view_idea(self):
        idea = self._get_selected_idea()
        if not idea:
            return
        from .report_view import IdeaReportWindow
        IdeaReportWindow(idea=idea, parent=self.get_root()).present()

    def _on_view_monthly(self):
        data = self._get_selected_month()
        if not data:
            return
        year, month, ideas_mes = data
        from .report_view import MonthlyReportWindow
        MonthlyReportWindow(ideas=ideas_mes, month=month, year=year, parent=self.get_root()).present()

    def _on_view_task(self):
        tarea = self._get_selected_tarea()
        if not tarea:
            return
        from .report_view import TaskReportWindow
        TaskReportWindow(tarea=tarea, parent=self.get_root()).present()

    # ── PDF handlers ─────────────────────────────────────────────────────────

    def _on_pdf_idea(self):
        idea = self._get_selected_idea()
        if not idea:
            return
        suggested = f"reporte_idea_{idea.nombre[:30].replace(' ', '_')}"
        self._save_pdf(
            lambda: self._gen_pdf_idea(idea),
            suggested,
        )

    def _on_pdf_monthly(self):
        data = self._get_selected_month()
        if not data:
            return
        year, month, ideas_mes = data
        month_str = datetime(year, month, 1).strftime("%B_%Y")
        self._save_pdf(
            lambda: self._gen_pdf_monthly(ideas_mes, month, year),
            f"reporte_mensual_{month_str}",
        )

    def _on_pdf_task(self):
        tarea = self._get_selected_tarea()
        if not tarea:
            return
        suggested = f"reporte_tarea_{tarea.nombre[:30].replace(' ', '_')}"
        self._save_pdf(
            lambda: self._gen_pdf_task(tarea),
            suggested,
        )

    # ── PDF generation + save dialog ────────────────────────────────────────

    def _save_pdf(self, generator_fn, suggested_name: str):
        """Generate PDF bytes then open FileDialog to save."""
        try:
            pdf_bytes = generator_fn()
        except Exception as e:
            self._show_toast(f"Error generando PDF: {e}")
            return

        from datetime import datetime as dt
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{suggested_name}_{timestamp}.pdf"

        pdf_filter = Gtk.FileFilter()
        pdf_filter.set_name("Archivos PDF")
        pdf_filter.add_mime_type("application/pdf")

        filters = Gio.ListStore(item_type=Gtk.FileFilter)
        filters.append(pdf_filter)

        from ..config import EXPORTS_DIR
        dialog = Gtk.FileDialog()
        dialog.set_title("Guardar reporte PDF")
        dialog.set_initial_name(filename)
        dialog.set_filters(filters)
        try:
            dialog.set_initial_folder(
                Gio.File.new_for_path(str(EXPORTS_DIR))
            )
        except Exception:
            pass

        def on_response(dlg, result):
            try:
                file = dlg.save_finish(result)
                if file is None:
                    return
                path = file.get_path()
                if not path.lower().endswith(".pdf"):
                    path += ".pdf"
                with open(path, "wb") as f:
                    f.write(pdf_bytes)
                toast = Adw.Toast(title="PDF guardado")
                toast.set_timeout(4)
                self._toast_overlay.add_toast(toast)
            except GLib.Error:
                pass  # User cancelled
            except Exception as e:
                self._show_toast(f"Error al guardar: {e}")

        dialog.save(self.get_root(), None, on_response)

    # ── Data helpers ─────────────────────────────────────────────────────────

    def _get_selected_idea(self):
        idx = self.idea_row.get_selected()
        if not self._idea_ids or not self._idea_ids[idx]:
            self._show_toast("No hay ideas registradas.")
            return None
        idea = load_idea(self._idea_ids[idx])
        if idea is None:
            self._show_toast("No se encontró la idea.")
        return idea

    def _get_selected_month(self):
        idx = self.mes_row.get_selected()
        if not self._mes_data or self._mes_data[idx] is None:
            self._show_toast("No hay datos para este período.")
            return None
        year, month = self._mes_data[idx]
        ideas_mes = [i for i in self._ideas if i.mes_registro() == (year, month)]
        return year, month, ideas_mes

    def _get_selected_tarea(self):
        idx = self.tarea_row.get_selected()
        if not self._tarea_ids or not self._tarea_ids[idx]:
            self._show_toast("No hay tareas registradas.")
            return None
        tarea = load_tarea(self._tarea_ids[idx])
        if tarea is None:
            self._show_toast("No se encontró la tarea.")
        return tarea

    def _gen_pdf_idea(self, idea):
        from ..pdf_generator import generate_detail_report
        return generate_detail_report(idea)

    def _gen_pdf_monthly(self, ideas, month, year):
        from ..pdf_generator import generate_monthly_report
        return generate_monthly_report(ideas, month, year)

    def _gen_pdf_task(self, tarea):
        from ..pdf_generator import generate_task_report
        return generate_task_report(tarea)

    def _show_toast(self, message: str):
        toast = Adw.Toast(title=message)
        toast.set_timeout(4)
        self._toast_overlay.add_toast(toast)
