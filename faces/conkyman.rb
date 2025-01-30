require 'gtk3'
require 'fileutils'
require 'open3'

# Obtener la ruta del directorio donde está el script
script_dir = File.dirname(File.expand_path(__FILE__))

# Definir la carpeta de temas relativa al directorio del script
themes_folder = File.join(script_dir, 'themes')

# Verificar si la carpeta existe
unless Dir.exist?(themes_folder)
  raise "No se encontró la carpeta 'themes' en #{themes_folder}"
end

# Obtener la lista de temas (sin extensión .lua)
themes = Dir.entries(themes_folder).select { |f| f.end_with?('.lua') }.map { |f| File.basename(f, '.lua') }

# Función para reemplazar .conkyrc
def replace_conkyrc(theme_name, themes_folder)
  conkyrc_path = File.join(Dir.home, '.conkyrc')
  theme_file = "#{theme_name}.lua"
  theme_path = File.join(themes_folder, theme_file)

  begin
    theme_content = File.read(theme_path, encoding: 'utf-8')
    File.write(conkyrc_path, theme_content, encoding: 'utf-8')

    dialog = Gtk::MessageDialog.new(
      nil,
      Gtk::Dialog::Flags::MODAL,
      Gtk::MessageType::INFO,
      Gtk::ButtonsType::OK,
      "Tema '#{theme_name}' aplicado correctamente."
    )
    dialog.run
    dialog.destroy
  rescue => e
    dialog = Gtk::MessageDialog.new(
      nil,
      Gtk::Dialog::Flags::MODAL,
      Gtk::MessageType::ERROR,
      Gtk::ButtonsType::OK,
      "Error al aplicar el tema: #{e.message}"
    )
    dialog.run
    dialog.destroy
  end
end

# Función para editar .conkyrc
def edit_conkyrc
  conkyrc_path = File.join(Dir.home, '.conkyrc')
  unless File.exist?(conkyrc_path)
    dialog = Gtk::MessageDialog.new(
      nil,
      Gtk::Dialog::Flags::MODAL,
      Gtk::MessageType::ERROR,
      Gtk::ButtonsType::OK,
      "No se encontró el archivo .conkyrc en #{conkyrc_path}."
    )
    dialog.run
    dialog.destroy
    return
  end

  begin
    Open3.popen3("gedit #{conkyrc_path}")
  rescue => e
    dialog = Gtk::MessageDialog.new(
      nil,
      Gtk::Dialog::Flags::MODAL,
      Gtk::MessageType::ERROR,
      Gtk::ButtonsType::OK,
      "Error al abrir gedit: #{e.message}"
    )
    dialog.run
    dialog.destroy
  end
end

# Crear la ventana principal
class ConkymanWindow < Gtk::Window
  def initialize(themes, themes_folder, script_dir)
    super(title: "Conkyman")

    set_default_size(300, 200)
    set_icon_from_file(File.join(script_dir, 'conkyman.svg')) if File.exist?(File.join(script_dir, 'conkyman.svg'))

    box = Gtk::Box.new(:vertical, 10)

    # Crear la barra de menú
    menu_bar = Gtk::MenuBar.new

    help_menu = Gtk::Menu.new
    help_menu_item = Gtk::MenuItem.new(label: "Ayuda")
    help_menu_item.set_submenu(help_menu)

    about_menu_item = Gtk::MenuItem.new(label: "Acerca de")
    about_menu_item.signal_connect("activate") { show_about_dialog(script_dir) }
    help_menu.append(about_menu_item)

    menu_bar.append(help_menu_item)
    box.pack_start(menu_bar, expand: false, fill: false, padding: 0)

    # Crear un combo box con los temas disponibles
    @theme_combo = Gtk::ComboBoxText.new
    themes.each { |theme| @theme_combo.append_text(theme) }
    @theme_combo.set_active(0)
    box.pack_start(@theme_combo, expand: false, fill: false, padding: 0)

    # Crear un botón para aplicar el tema
    apply_button = Gtk::Button.new(label: "Aplicar Tema")
    apply_button.signal_connect("clicked") do
      theme_name = @theme_combo.active_text
      replace_conkyrc(theme_name, themes_folder) if theme_name
    end
    box.pack_start(apply_button, expand: false, fill: false, padding: 0)

    # Crear un botón para editar .conkyrc
    edit_button = Gtk::Button.new(label: "Editar .conkyrc")
    edit_button.signal_connect("clicked") { edit_conkyrc }
    box.pack_start(edit_button, expand: false, fill: false, padding: 0)

    add(box)
    show_all
  end

  def show_about_dialog(script_dir)
    about_dialog = Gtk::AboutDialog.new
    about_dialog.program_name = "Yelena Conkyman"
    about_dialog.version = "1.0 v221224b Elena"
    about_dialog.comments = "Gestor de temas de Conky para CuerdOS GNU/Linux."
    about_dialog.license = "GPL-3.0"

    logo_path = File.join(script_dir, 'conkyman.svg')
    if File.exist?(logo_path)
      about_dialog.logo = GdkPixbuf::Pixbuf.new(file: logo_path).scale_simple(150, 150, :bilinear)
    end

    about_dialog.authors = [
      "Ale D.M ",
      "Leo H. Pérez (GatoVerde95)",
      "Pablo G.",
      "Welkis",
      "GatoVerde95 Studios",
      "CuerdOS Community",
      "Org. CuerdOS",
      "Stage 49"
    ]
    about_dialog.copyright = "© 2024 CuerdOS"

    about_dialog.run
    about_dialog.destroy
  end
end

# Iniciar la aplicación GTK
if __FILE__ == $PROGRAM_NAME
  Gtk.init
  window = ConkymanWindow.new(themes, themes_folder, script_dir)
  window.signal_connect("destroy") { Gtk.main_quit }
  Gtk.main
end
