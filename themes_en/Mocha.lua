--[[
CuerdOS conky based on Minimalis Conky 1.3
Author : CuerdOS
Release date : 22 Dec 2024
Tested on : Debian 12 - LXQt+Xfwm
Email : cuerdoslinux@proton.me
Optimizando hasta el último pixel
--]]

conky.config = {
    alignment = 'tr',
    background = true,
    border_width = 1,
    cpu_avg_samples = 32,
    default_color = '#8B4513',  -- Marrón (SaddleBrown)
    default_outline_color = '#A0522D',  -- Café medio (Sienna)
    default_shade_color = '#1C1C1C',  -- Gris oscuro (para contraste)
    color1 = '#D2B48C',  -- Café claro (Tan)
    double_buffer = true,
    draw_borders = false,
    draw_graph_borders = false,
    draw_outline = false,
    draw_shades = false,
    extra_newline = false,
    font = 'Roboto:size=9',  -- Usando la fuente Roboto
    gap_x = 25,
    gap_y = 50,
    minimum_height = 250,
    minimum_width = 220,
    net_avg_samples = 32,
    no_buffers = true,
    out_to_console = false,
    out_to_ncurses = false,
    out_to_stderr = false,
    out_to_x = true,
    own_window = true,
    own_window_class = 'Conky',
    own_window_transparent = true,
    own_window_argb_visual = true,
    own_window_type = 'desktop',
    own_window_hints = 'undecorated,sticky,skip_taskbar,skip_pager,below',
    show_graph_range = false,
    show_graph_scale = false,
    stippled_borders = 0,
    update_interval = 1.0,
    update_interval_on_battery = 300,
    uppercase = false,
    use_spacer = 'none',
    use_xft = true,
}

conky.text = [[
${color1}${goto 35}${font Roboto:size=19}${color}${time %H:%M}
${alignr}${goto 35}${font Roboto:size=12}${color}${time %a %d, %b %Y}
${color1}${goto 35}${font Roboto:size=12}${color}Hello! ${exec whoami}

${color1}${font ConkySymbols:size=16}f${font} ${voffset -10} System » $hr${color}
${color1}${goto 35}CPU% ${color}${freq_g}GHz ${alignr}${cpu cpu0}%${alignr}${cpubar cpu0 3,60}
${color1}${goto 35}Use ${color}$uptime_short ${alignr}${color1}

${color1}${font ConkySymbols:size=16}J${font} ${voffset -10} Memory » $hr${color}
${color1}${goto 35}RAM% ${color}$mem/$memmax ${alignr}
${color1}${goto 35}ZRAM% ${color}$swap/$swapmax ${alignr}

${color1}${font ConkySymbols:size=16}k${font} ${voffset -10} Disk » $hr${color}
${color1}${goto 35}Total occupied --> ${color}${fs_used /}/${fs_size /} ${goto 35}
${color1}${goto 35}Reading --> ${color}${diskio_read} ${goto 35}
${color1}${goto 35}Writing --> ${color}${diskio_write} ${goto 35}
${color1}${goto 35}${color}${exec hddtemp /dev/sda}
]]

