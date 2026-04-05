import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gio", "2.0")

from gi.repository import Gtk, Adw, Gio


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("IdeaTracker")
        self.set_default_size(1100, 700)
        self.set_size_request(800, 600)
        self.set_icon_name("IdeaTracker")   # taskbar + title bar icon
        self._build_ui()
        self._setup_actions()

    def _build_ui(self):
        # ToastOverlay wraps all content so toasts work app-wide
        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.toast_overlay.set_child(main_box)

        # ── View stack (3 main views) ──────────────────────────────────────
        self.view_stack = Adw.ViewStack()

        from .ideas_widget import IdeasWidget
        from .tareas_widget import TareasWidget
        from .reports_widget import ReportsWidget

        self.ideas_widget = IdeasWidget(toast_overlay=self.toast_overlay)
        self.tareas_widget = TareasWidget(toast_overlay=self.toast_overlay)
        self.reports_widget = ReportsWidget(toast_overlay=self.toast_overlay)

        self.view_stack.add_titled_with_icon(
            self.ideas_widget, "ideas", "Ideas", "document-edit-symbolic"
        )
        self.view_stack.add_titled_with_icon(
            self.tareas_widget, "tareas", "Tareas", "emblem-ok-symbolic"
        )
        self.view_stack.add_titled_with_icon(
            self.reports_widget, "reportes", "Reportes", "printer-symbolic"
        )

        # ── Header bar ────────────────────────────────────────────────────
        header_bar = Adw.HeaderBar()

        view_switcher = Adw.ViewSwitcher()
        view_switcher.set_stack(self.view_stack)
        view_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        header_bar.set_title_widget(view_switcher)

        # Primary action button (context-sensitive)
        self.btn_new = Gtk.Button(label="Nueva idea")
        self.btn_new.add_css_class("suggested-action")
        self.btn_new.set_tooltip_text("Nueva idea (Ctrl+N)")
        self.btn_new.connect("clicked", self._on_new_clicked)
        header_bar.pack_end(self.btn_new)

        # Overflow menu (⋮)
        menu_model = Gio.Menu()
        menu_model.append("Configuración", "win.preferences")
        sep = Gio.Menu()
        sep.append("Atajos de teclado", "win.show-shortcuts")
        sep.append("Acerca de IdeaTracker", "win.about")
        menu_model.append_section(None, sep)

        menu_btn = Gtk.MenuButton(
            menu_model=menu_model,
            icon_name="open-menu-symbolic",
            tooltip_text="Menú principal",
        )
        header_bar.pack_end(menu_btn)

        main_box.append(header_bar)
        main_box.append(self.view_stack)

        # Bottom ViewSwitcher bar (for narrow windows)
        switcher_bar = Adw.ViewSwitcherBar()
        switcher_bar.set_stack(self.view_stack)
        switcher_bar.set_reveal(False)
        main_box.append(switcher_bar)

        # Update header when view changes
        self.view_stack.connect("notify::visible-child", self._on_view_changed)
        self._on_view_changed(self.view_stack, None)

    # ── View change ────────────────────────────────────────────────────────

    def _on_view_changed(self, stack, _param):
        child_name = stack.get_visible_child_name()
        if child_name == "ideas":
            self.btn_new.set_label("Nueva idea")
            self.btn_new.set_tooltip_text("Nueva idea (Ctrl+N)")
            self.btn_new.set_visible(True)
            self.ideas_widget.refresh()
        elif child_name == "tareas":
            self.btn_new.set_label("Nueva tarea")
            self.btn_new.set_tooltip_text("Nueva tarea (Ctrl+N)")
            self.btn_new.set_visible(True)
            self.tareas_widget.refresh()
        elif child_name == "reportes":
            self.btn_new.set_visible(False)
            self.reports_widget.refresh()

    def _on_new_clicked(self, _button):
        child_name = self.view_stack.get_visible_child_name()
        if child_name == "ideas":
            self.ideas_widget.open_new_form()
        elif child_name == "tareas":
            self.tareas_widget.open_new_form()

    # ── Actions & keyboard shortcuts ────────────────────────────────────────

    def _setup_actions(self):
        app = self.get_application()

        def add_win_action(name, callback, accels=None):
            a = Gio.SimpleAction.new(name, None)
            a.connect("activate", callback)
            self.add_action(a)
            if accels:
                app.set_accels_for_action(f"win.{name}", accels)

        def add_app_action(name, callback, accels=None):
            a = Gio.SimpleAction.new(name, None)
            a.connect("activate", callback)
            app.add_action(a)
            if accels:
                app.set_accels_for_action(f"app.{name}", accels)

        add_win_action("new-item",       lambda *_: self._on_new_clicked(None), ["<ctrl>n"])
        add_win_action("refresh",        self._on_refresh,                       ["F5"])
        add_win_action("preferences",    self._on_preferences,                   ["<ctrl>comma"])
        add_win_action("show-shortcuts", self._on_show_shortcuts,                ["<ctrl>question"])
        add_win_action("about",          self._on_about)
        add_app_action("quit",           lambda *_: app.quit(),                  ["<ctrl>q"])

    # ── Action handlers ────────────────────────────────────────────────────

    def _on_refresh(self, _action, _param):
        child_name = self.view_stack.get_visible_child_name()
        if child_name == "ideas":
            self.ideas_widget.refresh()
        elif child_name == "tareas":
            self.tareas_widget.refresh()
        elif child_name == "reportes":
            self.reports_widget.refresh()

    def _on_preferences(self, _action, _param):
        from .config_widget import PreferencesWindow
        pref = PreferencesWindow(parent=self)
        pref.connect("categories-changed", self._on_categories_changed)
        pref.present()

    def _on_categories_changed(self, _win):
        self.ideas_widget.refresh_categories()
        self.reports_widget.refresh()

    def _on_about(self, _action, _param):
        about = Adw.AboutWindow(
            transient_for=self,
            application_name="IdeaTracker",
            application_icon="IdeaTracker",
            developer_name="IdeaTracker",
            version="1.3.0",
            comments="Gestión de ideas y planes de negocio.",
            license_type=Gtk.License.GPL_3_0,
            copyright="© 2024 IdeaTracker",
        )
        about.present()

    def _on_show_shortcuts(self, _action, _param):
        builder = Gtk.Builder.new_from_string("""
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <object class="GtkShortcutsWindow" id="shortcuts">
    <property name="modal">1</property>
    <child>
      <object class="GtkShortcutsSection">
        <property name="section-name">shortcuts</property>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title">Ideas y Tareas</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title">Nueva idea / tarea</property>
                <property name="accelerator">&lt;ctrl&gt;n</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title">Buscar</property>
                <property name="accelerator">&lt;ctrl&gt;f</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title">Actualizar lista</property>
                <property name="accelerator">F5</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title">Configuración</property>
                <property name="accelerator">&lt;ctrl&gt;comma</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title">Atajos de teclado</property>
                <property name="accelerator">&lt;ctrl&gt;question</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title">Salir</property>
                <property name="accelerator">&lt;ctrl&gt;q</property>
              </object>
            </child>
          </object>
        </child>
      </object>
    </child>
  </object>
</interface>
""", -1)
        shortcuts = builder.get_object("shortcuts")
        shortcuts.set_transient_for(self)
        shortcuts.present()
