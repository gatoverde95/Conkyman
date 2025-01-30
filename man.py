import os
import gi
import subprocess

os.environ['GDK_BACKEND'] = 'x11'

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

# Centralizar la obtención del path del archivo .conkyrc
def get_conkyrc_path():
    return os.path.expanduser('~') + '/.conkyrc'

# Centralizar la función show_dialog
def show_dialog(title, message, message_type):
    dialog = Gtk.MessageDialog(
        transient_for=None,
        modal=True,
        message_type=message_type,
        buttons=Gtk.ButtonsType.OK,
        text=message
    )
    dialog.set_title(title)
    dialog.run()
    dialog.destroy()

# Detectar si estamos en Wayland o X11
def detect_graphics_backend():
    session_type = os.getenv('XDG_SESSION_TYPE', '').lower()
    if session_type == 'wayland':
        print("Detectado Wayland")
    else:
        print("Detectado X11, usando backend X11")
        os.environ['GDK_BACKEND'] = 'x11'

detect_graphics_backend()

script_dir = os.path.dirname(os.path.abspath(__file__))
themes_folder = os.path.join(script_dir, '/usr/share/conkyman/themes')

if not os.path.exists(themes_folder):
    raise FileNotFoundError(f'No se encontró la carpeta "themes" en {themes_folder}')

def list_themes():
    return [os.path.splitext(f)[0] for f in os.listdir(themes_folder) if f.endswith('.lua')]

themes = list_themes()

def read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)

def replace_conkyrc(theme_name):
    conkyrc_path = get_conkyrc_path()
    theme_file = theme_name + '.lua'
    theme_path = os.path.join(themes_folder, theme_file)

    try:
        theme_content = read_file(theme_path)
        write_file(conkyrc_path, theme_content)
        show_dialog("Aviso!", f'Tema "{theme_name}" aplicado correctamente.', Gtk.MessageType.INFO)
        restart_conky()
    except Exception as e:
        show_dialog("Aviso!", f'Error al aplicar el tema: {str(e)}', Gtk.MessageType.ERROR)

def is_conky_running():
    try:
        result = subprocess.run(["pgrep", "conky"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        pids = result.stdout.split()
        return len(pids) > 0
    except Exception as e:
        show_dialog("Aviso!", f'Error al verificar Conky: {str(e)}', Gtk.MessageType.ERROR)
        return False

def kill_conky():
    try:
        subprocess.run(["pkill", "conky"], check=True)
    except subprocess.CalledProcessError as e:
        show_dialog("Aviso!", f'Error al matar Conky: {str(e)}', Gtk.MessageType.ERROR)

def restart_conky():
    is_running = is_conky_running()
    if is_running:
        kill_conky()

    try:
        subprocess.Popen(["conky", "-d"], start_new_session=True)
        show_dialog("Aviso!", 'Conky reiniciado correctamente.', Gtk.MessageType.INFO)
    except Exception as e:
        show_dialog("Aviso!", f'Error al reiniciar Conky: {str(e)}', Gtk.MessageType.ERROR)

def start_conky():
    is_running = is_conky_running()
    if is_running:
        show_dialog("Aviso!", 'Conky ya está en ejecución.', Gtk.MessageType.INFO)
    else:
        try:
            subprocess.Popen(["conky", "-d"], start_new_session=True)
            show_dialog("Aviso!", 'Conky iniciado correctamente.', Gtk.MessageType.INFO)
        except Exception as e:
            show_dialog("Aviso!", f'Error al iniciar Conky: {str(e)}', Gtk.MessageType.ERROR)

class ConkymanWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Conkyman")

        self.set_decorated(True)
        icon_path = os.path.join(script_dir, "/usr/share/conkyman/icons/conkyman.svg")
        if os.path.exists(icon_path):
            self.set_icon_from_file(icon_path)

        self.set_default_size(600, 400)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        menubar = Gtk.MenuBar()
        conky_menu = Gtk.MenuItem(label="Conky")
        conky_submenu = Gtk.Menu()
        conky_menu.set_submenu(conky_submenu)

        start_item = Gtk.MenuItem(label="Iniciar Conky")
        start_item.connect("activate", self.on_start_button_clicked)
        conky_submenu.append(start_item)

        restart_item = Gtk.MenuItem(label="Reiniciar Conky")
        restart_item.connect("activate", self.on_restart_button_clicked)
        conky_submenu.append(restart_item)

        menubar.append(conky_menu)

        about_menu = Gtk.MenuItem(label="Acerca de")
        about_menu.connect("activate", self.show_about_dialog)
        menubar.append(about_menu)

        box.pack_start(menubar, False, False, 0)

        notebook = Gtk.Notebook()

        # Pestaña de Temas
        themes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.theme_combo = Gtk.ComboBoxText()
        for theme in themes:
            self.theme_combo.append_text(theme)
        self.theme_combo.set_active(0)
        themes_box.pack_start(Gtk.Label(label="Selecciona un tema:"), False, False, 0)
        themes_box.pack_start(self.theme_combo, False, False, 0)

        self.theme_image = Gtk.Image()
        themes_box.pack_start(self.theme_image, True, True, 0)

        apply_button = Gtk.Button(label="Aplicar Tema")
        apply_button.connect("clicked", self.on_apply_button_clicked)
        themes_box.pack_start(apply_button, False, False, 0)

        notebook.append_page(themes_box, Gtk.Label(label="Temas"))

        # Pestaña de Posición
        position_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.alignment_combo = Gtk.ComboBoxText()
        self.alignment_combo.append_text("top_right")
        self.alignment_combo.append_text("top_left")
        self.alignment_combo.append_text("bottom_right")
        self.alignment_combo.append_text("bottom_left")
        self.alignment_combo.append_text("top_middle")
        self.alignment_combo.append_text("bottom_middle")
        self.alignment_combo.set_active(0)
        position_box.pack_start(Gtk.Label(label="Posición General:"), False, False, 0)
        position_box.pack_start(self.alignment_combo, False, False, 0)

        gap_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.gap_x_spin = Gtk.SpinButton()
        self.gap_x_spin.set_range(-2000, 2000)
        self.gap_x_spin.set_increments(1, 10)
        self.gap_x_spin.set_value(0)
        gap_box.pack_start(Gtk.Label(label="gap_x:"), False, False, 0)
        gap_box.pack_start(self.gap_x_spin, False, False, 0)

        self.gap_y_spin = Gtk.SpinButton()
        self.gap_y_spin.set_range(-2000, 2000)
        self.gap_y_spin.set_increments(1, 10)
        self.gap_y_spin.set_value(0)
        gap_box.pack_start(Gtk.Label(label="gap_y:"), False, False, 0)
        gap_box.pack_start(self.gap_y_spin, False, False, 0)

        position_box.pack_start(gap_box, False, False, 0)

        move_button = Gtk.Button(label="Mover Conky")
        move_button.connect("clicked", self.on_move_button_clicked)
        position_box.pack_start(move_button, False, False, 0)

        # Botón para establecer posición predeterminada
        default_button = Gtk.Button(label="Posición Predeterminada")
        default_button.connect("clicked", self.on_default_button_clicked)
        position_box.pack_start(default_button, False, False, 0)

        notebook.append_page(position_box, Gtk.Label(label="Posición"))

        box.pack_start(notebook, True, True, 0)
        self.add(box)
        self.show_all()

        self.check_conkyrc()

        self.theme_combo.connect("changed", self.on_theme_combo_changed)
        self.update_theme_image()

    def check_conkyrc(self):
        conkyrc_path = get_conkyrc_path()
        if not os.path.exists(conkyrc_path):
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text='No se encontró el archivo .conkyrc. ¿Desea generarlo automáticamente?'
            )
            dialog.set_title("Aviso!")
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                self.generate_conkyrc()

    def generate_conkyrc(self):
        conkyrc_path = get_conkyrc_path()
        gen_lua_path = os.path.join(script_dir, '/usr/share/conkyman/generic/gen.lua')

        try:
            gen_content = read_file(gen_lua_path)
            write_file(conkyrc_path, gen_content)
            show_dialog("Aviso!", 'Archivo .conkyrc generado correctamente.', Gtk.MessageType.INFO)
            start_conky()
        except Exception as e:
            show_dialog("Aviso!", f'Error al generar el archivo .conkyrc: {str(e)}', Gtk.MessageType.ERROR)

    def on_apply_button_clicked(self, widget):  # pylint: disable=unused-argument
        theme_name = self.theme_combo.get_active_text()
        if theme_name:
            replace_conkyrc(theme_name)
            self.update_theme_image()

    def on_move_button_clicked(self, widget):  # pylint: disable=unused-argument
        alignment = self.alignment_combo.get_active_text()
        gap_x = int(self.gap_x_spin.get_value())
        gap_y = int(self.gap_y_spin.get_value())
        if alignment:
            self.move_conky(alignment, gap_x, gap_y)

    def on_default_button_clicked(self, widget):  # pylint: disable=unused-argument
        self.move_conky('top_right', 30, 40)

    def move_conky(self, alignment, gap_x, gap_y):
        conkyrc_path = get_conkyrc_path()
        if not os.path.exists(conkyrc_path):
            show_dialog("Aviso!", f'No se encontró el archivo .conkyrc en {conkyrc_path}.', Gtk.MessageType.ERROR)
            return

        try:
            content = read_file(conkyrc_path).splitlines()

            new_content = []
            for line in content:
                if line.strip().startswith("alignment"):
                    new_content.append(f"alignment = '{alignment}',\n")
                elif line.strip().startswith("gap_x"):
                    new_content.append(f"gap_x = {gap_x},\n")
                elif line.strip().startswith("gap_y"):
                    new_content.append(f"gap_y = {gap_y},\n")
                else:
                    new_content.append(line + '\n')

            write_file(conkyrc_path, ''.join(new_content))
            show_dialog("Aviso!", 'Posición de Conky actualizada correctamente.', Gtk.MessageType.INFO)
            restart_conky()
        except Exception as e:
            show_dialog("Aviso!", f'Error al actualizar la posición: {str(e)}', Gtk.MessageType.ERROR)

    def on_start_button_clicked(self, widget):  # pylint: disable=unused-argument
        start_conky()

    def on_restart_button_clicked(self, widget):  # pylint: disable=unused-argument
        restart_conky()

    def on_theme_combo_changed(self, widget):  # pylint: disable=unused-argument
        self.update_theme_image()

    def update_theme_image(self):
        theme_name = self.theme_combo.get_active_text()
        if theme_name:
            image_path = os.path.join(themes_folder, f"{theme_name}.png")
            if os.path.exists(image_path):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
                self.theme_image.set_from_pixbuf(pixbuf)
            else:
                self.theme_image.set_from_stock(Gtk.STOCK_MISSING_IMAGE, Gtk.IconSize.DIALOG)

    def show_about_dialog(self, widget):  # pylint: disable=unused-argument
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name("Yelena Conkyman")
        about_dialog.set_version("1.0 v100125a Elena")
        about_dialog.set_comments("Gestor de temas de Conky para CuerdOS GNU/Linux.")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)

        logo_path = os.path.join(script_dir, "/usr/share/conkyman/icons/conkyman.svg")
        about_dialog.set_authors([
            "Ale D.M ",
            "Leo H. Pérez (GatoVerde95)",
            "Pablo G.",
            "Welkis",
            "GatoVerde95 Studios",
            "CuerdOS Community"
        ])
        about_dialog.set_copyright("© 2025 CuerdOS")

        if os.path.exists(logo_path):
            logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file(logo_path)
            logo_pixbuf = logo_pixbuf.scale_simple(150, 150, GdkPixbuf.InterpType.BILINEAR)
            about_dialog.set_logo(logo_pixbuf)

        about_dialog.run()
        about_dialog.destroy()

if __name__ == "__main__":
    window = ConkymanWindow()
    window.connect("destroy", Gtk.main_quit)
    Gtk.main()
