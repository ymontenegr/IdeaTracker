"""
Native GTK4 report viewer.
Provides builder functions that return scrollable content widgets,
plus thin Window wrappers that still work as standalone dialogs.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

from ..models import Idea, Tarea
from ..config import STATUS_LIST, TAREA_STATUS_LIST


# ── Badge helpers ─────────────────────────────────────────────────────────────

STATUS_BADGE = {
    "Por iniciar": "badge-blue",
    "Iniciado":    "badge-yellow",
    "En proceso":  "badge-orange",
    "Finalizado":  "badge-green",
    "Postergado":  "badge-gray",
    "Cancelado":   "badge-red",
    "Iniciada":    "badge-yellow",
    "Cerrada":     "badge-gray",
}
PRIORIDAD_BADGE = {
    "Alta":  "badge-red",
    "Media": "badge-orange",
    "Baja":  "badge-green",
}


def _make_badge(text: str, css_class: str) -> Gtk.Label:
    badge = Gtk.Label(label=text)
    badge.add_css_class("status-badge")
    badge.add_css_class(css_class)
    badge.set_valign(Gtk.Align.CENTER)
    return badge


def _action_row(title: str, value: str) -> Adw.ActionRow:
    row = Adw.ActionRow(title=title)
    lbl = Gtk.Label(label=value or "—")
    lbl.add_css_class("dim-label")
    lbl.set_wrap(True)
    lbl.set_max_width_chars(60)
    lbl.set_valign(Gtk.Align.CENTER)
    lbl.set_halign(Gtk.Align.END)
    row.add_suffix(lbl)
    return row


# ══════════════════════════════════════════════════════════════════════════════
#  Content builder functions (return scrollable widgets, no window wrapper)
# ══════════════════════════════════════════════════════════════════════════════

def build_idea_report_widget(idea: Idea) -> Gtk.ScrolledWindow:
    """Returns a scrollable widget with the full idea report."""
    scroll = Gtk.ScrolledWindow()
    scroll.set_vexpand(True)
    scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

    clamp = Adw.Clamp()
    clamp.set_maximum_size(740)
    clamp.set_margin_start(12)
    clamp.set_margin_end(12)
    clamp.set_margin_top(16)
    clamp.set_margin_bottom(24)

    content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
    clamp.set_child(content)
    scroll.set_child(clamp)
    _fill_idea_content(content, idea)
    return scroll


def build_monthly_report_widget(ideas, month_name: str) -> Gtk.ScrolledWindow:
    """Returns a scrollable widget with the monthly ideas report."""
    scroll = Gtk.ScrolledWindow()
    scroll.set_vexpand(True)
    scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

    clamp = Adw.Clamp()
    clamp.set_maximum_size(780)
    clamp.set_margin_start(12)
    clamp.set_margin_end(12)
    clamp.set_margin_top(16)
    clamp.set_margin_bottom(24)

    content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
    clamp.set_child(content)
    scroll.set_child(clamp)
    _fill_monthly_content(content, ideas, month_name)
    return scroll


def build_task_report_widget(tarea: Tarea) -> Gtk.ScrolledWindow:
    """Returns a scrollable widget with the task report."""
    scroll = Gtk.ScrolledWindow()
    scroll.set_vexpand(True)
    scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

    clamp = Adw.Clamp()
    clamp.set_maximum_size(700)
    clamp.set_margin_start(12)
    clamp.set_margin_end(12)
    clamp.set_margin_top(16)
    clamp.set_margin_bottom(24)

    content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
    clamp.set_child(content)
    scroll.set_child(clamp)
    _fill_task_content(content, tarea)
    return scroll


# ══════════════════════════════════════════════════════════════════════════════
#  Internal content fillers
# ══════════════════════════════════════════════════════════════════════════════

def _fill_idea_content(content: Gtk.Box, idea: Idea):
    # ── Hero card ─────────────────────────────────────────────────────────
    hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    hero.add_css_class("card")
    hero.set_margin_bottom(4)

    inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    inner.set_margin_start(18)
    inner.set_margin_end(18)
    inner.set_margin_top(16)
    inner.set_margin_bottom(16)

    name_lbl = Gtk.Label(label=idea.nombre)
    name_lbl.add_css_class("title-2")
    name_lbl.set_halign(Gtk.Align.START)
    name_lbl.set_wrap(True)
    inner.append(name_lbl)

    badges_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    badges_row.append(_make_badge(idea.estatus,         STATUS_BADGE.get(idea.estatus, "badge-gray")))
    badges_row.append(_make_badge(idea.prioridad,       PRIORIDAD_BADGE.get(idea.prioridad, "badge-gray")))
    badges_row.append(_make_badge(idea.categoria_nombre, "badge-blue"))
    inner.append(badges_row)

    hero.append(inner)
    content.append(hero)

    # ── Información general ───────────────────────────────────────────────
    grp1 = Adw.PreferencesGroup(title="Información general")
    grp1.add(_action_row("Origen",               idea.origen))
    grp1.add(_action_row("Fecha de registro",    idea.fecha_registro_display()))
    grp1.add(_action_row("Fecha probable inicio", idea.fecha_inicio_display()))
    content.append(grp1)

    # ── Descripción ───────────────────────────────────────────────────────
    grp_desc = Adw.PreferencesGroup(title="Descripción")
    desc_lbl = Gtk.Label(label=idea.descripcion or "—")
    desc_lbl.set_wrap(True)
    desc_lbl.set_halign(Gtk.Align.START)
    desc_lbl.set_margin_start(12)
    desc_lbl.set_margin_end(12)
    desc_lbl.set_margin_top(10)
    desc_lbl.set_margin_bottom(10)
    desc_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    desc_card.add_css_class("card")
    desc_card.append(desc_lbl)
    grp_desc.add(desc_card)
    content.append(grp_desc)

    # ── Costos y retorno ──────────────────────────────────────────────────
    grp2 = Adw.PreferencesGroup(title="Costos y retorno")
    grp2.add(_action_row("Costo aproximado", idea.costo_display()))
    content.append(grp2)

    grp_ben = Adw.PreferencesGroup(title="Beneficio esperado")
    ben_lbl = Gtk.Label(label=idea.beneficio_esperado or "—")
    ben_lbl.set_wrap(True)
    ben_lbl.set_halign(Gtk.Align.START)
    ben_lbl.set_margin_start(12)
    ben_lbl.set_margin_end(12)
    ben_lbl.set_margin_top(10)
    ben_lbl.set_margin_bottom(10)
    ben_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    ben_card.add_css_class("card")
    ben_card.append(ben_lbl)
    grp_ben.add(ben_card)
    content.append(grp_ben)

    # ── Notas ─────────────────────────────────────────────────────────────
    notas = idea.notas or []
    grp_notas = Adw.PreferencesGroup(title=f"Notas ({len(notas)})")
    if notas:
        lb = Gtk.ListBox()
        lb.add_css_class("boxed-list")
        lb.set_selection_mode(Gtk.SelectionMode.NONE)
        for nota in reversed(notas):
            row = Adw.ActionRow(title=nota.texto, subtitle=nota.fecha_display())
            lb.append(row)
        grp_notas.add(lb)
    else:
        grp_notas.add(Adw.ActionRow(title="Sin notas registradas"))
    content.append(grp_notas)


def _fill_monthly_content(content: Gtk.Box, ideas, month_name: str):
    # ── Hero card ─────────────────────────────────────────────────────────
    hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    hero.add_css_class("card")
    inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    inner.set_margin_start(18)
    inner.set_margin_end(18)
    inner.set_margin_top(16)
    inner.set_margin_bottom(16)

    title_lbl = Gtk.Label(label=f"Reporte mensual — {month_name}")
    title_lbl.add_css_class("title-2")
    title_lbl.set_halign(Gtk.Align.START)
    inner.append(title_lbl)

    count_lbl = Gtk.Label(label=f"Total de ideas: {len(ideas)}")
    count_lbl.add_css_class("dim-label")
    count_lbl.set_halign(Gtk.Align.START)
    inner.append(count_lbl)
    hero.append(inner)
    content.append(hero)

    # ── Ideas list ────────────────────────────────────────────────────────
    grp = Adw.PreferencesGroup(title="Ideas registradas")
    if not ideas:
        grp.add(Adw.ActionRow(title="Sin ideas en este período"))
    else:
        lb = Gtk.ListBox()
        lb.add_css_class("boxed-list")
        lb.set_selection_mode(Gtk.SelectionMode.NONE)
        for idea in sorted(ideas, key=lambda i: i.fecha_registro):
            exp = Adw.ExpanderRow(
                title=idea.nombre,
                subtitle=f"{idea.categoria_nombre}  ·  {idea.fecha_registro_display()}",
            )
            exp.add_row(_action_row("Prioridad",    idea.prioridad))
            exp.add_row(_action_row("Estatus",      idea.estatus))
            exp.add_row(_action_row("Fecha inicio", idea.fecha_inicio_display()))
            exp.add_row(_action_row("Costo",        idea.costo_display()))
            exp.add_prefix(_make_badge(idea.estatus, STATUS_BADGE.get(idea.estatus, "badge-gray")))
            lb.append(exp)
        grp.add(lb)
    content.append(grp)

    # ── Resumen por estatus ───────────────────────────────────────────────
    from collections import Counter
    counts = Counter(i.estatus for i in ideas)
    grp_sum = Adw.PreferencesGroup(title="Resumen por estatus")
    lb2 = Gtk.ListBox()
    lb2.add_css_class("boxed-list")
    lb2.set_selection_mode(Gtk.SelectionMode.NONE)
    for estatus in STATUS_LIST:
        n = counts.get(estatus, 0)
        if n == 0:
            continue
        row = Adw.ActionRow(title=estatus)
        row.add_suffix(_make_badge(str(n), STATUS_BADGE.get(estatus, "badge-gray")))
        lb2.append(row)
    grp_sum.add(lb2)
    content.append(grp_sum)


def _fill_task_content(content: Gtk.Box, tarea: Tarea):
    # ── Hero card ─────────────────────────────────────────────────────────
    hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    hero.add_css_class("card")
    inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    inner.set_margin_start(18)
    inner.set_margin_end(18)
    inner.set_margin_top(16)
    inner.set_margin_bottom(16)

    name_lbl = Gtk.Label(label=tarea.nombre)
    name_lbl.add_css_class("title-2")
    name_lbl.set_halign(Gtk.Align.START)
    name_lbl.set_wrap(True)
    inner.append(name_lbl)

    badges = Gtk.Box(spacing=8)
    badges.append(_make_badge(tarea.estatus, STATUS_BADGE.get(tarea.estatus, "badge-gray")))
    inner.append(badges)
    hero.append(inner)
    content.append(hero)

    # ── Información ───────────────────────────────────────────────────────
    grp1 = Adw.PreferencesGroup(title="Información")
    grp1.add(_action_row("Proyecto / Idea",   tarea.idea_nombre))
    grp1.add(_action_row("Fecha de creación", tarea.fecha_creacion_display()))
    grp1.add(_action_row("Último cambio",     tarea.fecha_ultimo_cambio_display()))
    content.append(grp1)

    if tarea.descripcion:
        grp_desc = Adw.PreferencesGroup(title="Descripción")
        desc_lbl = Gtk.Label(label=tarea.descripcion)
        desc_lbl.set_wrap(True)
        desc_lbl.set_halign(Gtk.Align.START)
        desc_lbl.set_margin_start(12)
        desc_lbl.set_margin_end(12)
        desc_lbl.set_margin_top(10)
        desc_lbl.set_margin_bottom(10)
        desc_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        desc_card.add_css_class("card")
        desc_card.append(desc_lbl)
        grp_desc.add(desc_card)
        content.append(grp_desc)

    # ── Historial de estatus ──────────────────────────────────────────────
    historial = tarea.historial_estatus or []
    grp_h = Adw.PreferencesGroup(title=f"Historial de estatus ({len(historial)} cambios)")
    if historial:
        lb = Gtk.ListBox()
        lb.add_css_class("boxed-list")
        lb.set_selection_mode(Gtk.SelectionMode.NONE)
        for h in reversed(historial):
            row = Adw.ActionRow(title=h.estatus, subtitle=h.fecha_display())
            row.add_prefix(_make_badge("●", STATUS_BADGE.get(h.estatus, "badge-gray")))
            lb.append(row)
        grp_h.add(lb)
    else:
        grp_h.add(Adw.ActionRow(title="Sin historial registrado"))
    content.append(grp_h)

    # ── Notas ─────────────────────────────────────────────────────────────
    notas = tarea.notas or []
    grp_n = Adw.PreferencesGroup(title=f"Notas ({len(notas)})")
    if notas:
        lb2 = Gtk.ListBox()
        lb2.add_css_class("boxed-list")
        lb2.set_selection_mode(Gtk.SelectionMode.NONE)
        for nota in reversed(notas):
            lb2.append(Adw.ActionRow(title=nota.texto, subtitle=nota.fecha_display()))
        grp_n.add(lb2)
    else:
        grp_n.add(Adw.ActionRow(title="Sin notas registradas"))
    content.append(grp_n)


# ══════════════════════════════════════════════════════════════════════════════
#  Standalone window wrappers (kept for backward compatibility)
# ══════════════════════════════════════════════════════════════════════════════

class IdeaReportWindow(Adw.Window):
    def __init__(self, idea: Idea, parent=None):
        super().__init__(transient_for=parent, modal=True)
        self.set_title(f"Reporte — {idea.nombre}")
        self.set_default_size(760, 660)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        header = Adw.HeaderBar()
        btn_close = Gtk.Button(label="Cerrar")
        btn_close.add_css_class("flat")
        btn_close.connect("clicked", lambda _: self.close())
        header.pack_start(btn_close)
        main_box.append(header)
        main_box.append(build_idea_report_widget(idea))


class MonthlyReportWindow(Adw.Window):
    def __init__(self, ideas, month: int, year: int, parent=None):
        from datetime import datetime
        month_name = datetime(year, month, 1).strftime("%B %Y").capitalize()
        super().__init__(transient_for=parent, modal=True)
        self.set_title(f"Reporte mensual — {month_name}")
        self.set_default_size(800, 660)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        header = Adw.HeaderBar()
        btn_close = Gtk.Button(label="Cerrar")
        btn_close.add_css_class("flat")
        btn_close.connect("clicked", lambda _: self.close())
        header.pack_start(btn_close)
        main_box.append(header)
        main_box.append(build_monthly_report_widget(ideas, month_name))


class TaskReportWindow(Adw.Window):
    def __init__(self, tarea: Tarea, parent=None):
        super().__init__(transient_for=parent, modal=True)
        self.set_title(f"Reporte — {tarea.nombre}")
        self.set_default_size(720, 600)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        header = Adw.HeaderBar()
        btn_close = Gtk.Button(label="Cerrar")
        btn_close.add_css_class("flat")
        btn_close.connect("clicked", lambda _: self.close())
        header.pack_start(btn_close)
        main_box.append(header)
        main_box.append(build_task_report_widget(tarea))
