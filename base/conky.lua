local lgi = require('lgi')
local Gtk = lgi.Gtk
local Gio = lgi.Gio
local GLib = lgi.GLib

-- Inicializar GTK
Gtk.init()

-- Obtener la ruta del directorio donde está el script
local script_dir = debug.getinfo(1, 'S').source:match("^@(.+/)")

-- Definir la carpeta de temas relativa al directorio del script
local themes_folder = script_dir .. 'themes/'

-- Verificar si la carpeta existe
local file = Gio.File.new_for_path(themes_folder)
if not file:query_exists(nil) then
  error("No se encontró la carpeta 'themes' en " .. themes_folder)
end

-- Obtener la lista de temas (sin extensión .lua)
local themes = {}
for file in lfs.dir(themes_folder) do
  if file:match('%.lua$') then
    table.insert(themes, file:gsub('%.lua$', ''))
  end
end

-- Función para reemplazar .conkyrc
local function replace_conkyrc(theme_name)
  local conkyrc_path = GLib.get_home_dir() .. '/.conkyrc'
  local theme_file = themes_folder .. theme_name .. '.lua'

  local theme_content, err = GLib.file_get_contents(theme_file)
  if not theme_content then
    local dialog = Gtk.MessageDialog {
      message_type = Gtk.MessageType.ERROR,
      buttons = Gtk.ButtonsType.OK,
      text = "Error al leer el tema: " .. err
    }
    dialog:run()
    dialog:destroy()
    return
  end

  local success, write_err = GLib.file_set_contents(conkyrc_path, theme_content)
  if not success then
    local dialog = Gtk.MessageDialog {
      message_type = Gtk.MessageType.ERROR,
      buttons = Gtk.ButtonsType.OK,
      text = "Error al escribir en .conkyrc: " .. write_err
    }
    dialog:run()
    dialog:destroy()
  else
    local dialog = Gtk.MessageDialog {
      message_type = Gtk.MessageType.INFO,
      buttons = Gtk.ButtonsType.OK,
      text = "Tema '" .. theme_name .. "' aplicado correctamente."
    }
    dialog:run()
    dialog:destroy()
  end
end

-- Función para editar .conkyrc
local function edit_conkyrc()
  local conkyrc_path = GLib.get_home_dir() .. '/.conkyrc'

  if not GLib.file_test(conkyrc_path, GLib.FileTest.EXISTS) then
    local dialog = Gtk.MessageDialog {
      message_type = Gtk.MessageType.ERROR,
      buttons = Gtk.ButtonsType.OK,
      text = "No se encontró el archivo .conkyrc en " .. conkyrc_path
    }
    dialog:run()
    dialog:destroy()
    return
  end

  local _, err = GLib.spawn_command_line_async('gedit ' .. conkyrc_path)
  if err then
    local dialog = Gtk.MessageDialog {
      message_type = Gtk.MessageType.ERROR,
      buttons = Gtk.ButtonsType.OK,
      text = "Error al abrir gedit: " .. err
    }
    dialog:run()
    dialog:destroy()
  end
end

-- Crear la ventana principal
local function create_main_window()
  local window = Gtk.Window {
    title = "Conkyman",
    default_width = 300,
    default_height = 200,
    on_destroy = Gtk.main_quit
  }

  local box = Gtk.Box {
    orientation = Gtk.Orientation.VERTICAL,
    spacing = 10,
    margin = 10
  }

  -- Crear un combo box con los temas disponibles
  local theme_combo = Gtk.ComboBoxText()
  for _, theme in ipairs(themes) do
    theme_combo:append_text(theme)
  end
  theme_combo.active = 0
  box:pack_start(theme_combo, false, false, 0)

  -- Crear un botón para aplicar el tema
  local apply_button = Gtk.Button {
    label = "Aplicar Tema",
    on_clicked = function()
      local theme_name = theme_combo:get_active_text()
      if theme_name then
        replace_conkyrc(theme_name)
      end
    end
  }
  box:pack_start(apply_button, false, false, 0)

  -- Crear un botón para editar .conkyrc
  local edit_button = Gtk.Button {
    label = "Editar .conkyrc",
    on_clicked = edit_conkyrc
  }
  box:pack_start(edit_button, false, false, 0)

  window:add(box)
  window:show_all()
end

-- Iniciar la aplicación GTK
create_main_window()
Gtk.main()
