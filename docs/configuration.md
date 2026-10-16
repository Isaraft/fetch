# Configuration

FFetch-3D is configured through `~/.config/ffetch-3d/config`. If the file doesn't exist, all fields are shown in the default order.

The directory follows `$XDG_CONFIG_HOME/ffetch-3d` when `XDG_CONFIG_HOME` is
absolute; otherwise it uses `$HOME/.config/ffetch-3d`. `--config PATH` selects
an explicit file. CLI settings override configuration; launchers never write
this file. An existing config controls field order, including an empty file.

```ini
logo_outer=rgb:0:255:255
logo_inner=rgb:0:255:255
label_color=rgb:0:255:255
```

RGB components must have one to three decimal digits, each in 0–255. Invalid
colors are diagnosed and ignored, retaining the previous value. CLI colors
are strict and cause failure on invalid input. `--color VALUE` sets all three;
`--logo-outer`, `--logo-inner`, and `--label-color` set individual colors.
Later color flags override earlier ones.

## Fields

List field names one per line to show them, in the order you want. Comment out or remove fields to hide them. If a config file exists, only the fields listed in it are shown.

```
os
host
kernel
uptime
packages
shell
display
wm
theme
icons
font
cursor
terminal
cpu
gpu
memory
swap
disk
ip
battery
locale
colors
```

All fields are optional. You can reorder them however you want.

## Separators

Add `---` on its own line to insert a blank line between groups of fields:

```
os
host
kernel
---
cpu
gpu
memory
```

## Custom fields

Add static text fields with `custom_Label=value`:

```
custom_Pronouns=he/him
custom_Website=example.com
custom_Editor=neovim
```

These render like built-in fields (`Pronouns: he/him`) with the configured label color. You can place them anywhere in the field list and mix them with separators. No command execution — values are static strings only.

## Appearance

```
label_color=magenta
```

Color of the labels (the "CPU:", "Memory:", etc. text). Accepts: `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, an ANSI SGR number from 0 to 107, or `rgb:R:G:B` (each component 0–255).

```
separator=-
```

Character used for the title separator line. Default is `-`.

```
box=1
```

Draw a Unicode box around the system info. `0` = off (default), `1` = on. Also accepts `yes`/`no`/`true`/`false`.

```
shading=.,-~:;=!*#$@
```

Custom shading ramp for the 3D rendering. Characters go from dimmest to brightest. Supports UTF-8. This implies ASCII shading mode.

```
shading_mode=ascii
```

Shading mode. `ascii` (default) uses the character ramp. `blocks` uses 2x2 quadrant blocks. `sextants` uses 2x3 sub-cell blocks for the sharpest edges (requires suitable terminal/font glyph support). See [shading-modes.md](shading-modes.md).

## Logo colors

Explicit surface colors override embedded logo colors. Without an override, embedded colors remain available. Set two-tone coloring with:

```
logo_outer=magenta
logo_inner=white
```

`logo_outer` is the extruded side color, `logo_inner` is the front/back face color. Accepts the same color names, numeric SGR values, and RGB syntax as `label_color`.

## 3D settings

```
light=top-left
```

Light direction. Options: `top-left` (default), `top-right`, `top`, `left`, `right`, `front`, `bottom-left`, `bottom-right`.

```
spin=xy
```

Which axes to rotate around. `x`, `y`, or `xy` (default).

```
speed=1.0
```

Rotation speed multiplier. Higher = faster.

```
size=1.0
```

Logo scale. `2.0` for double size, `0.5` for half. Range: 0.5 to 5.0.

```
depth=1.0
```

3D extrusion depth. Higher = chunkier relief. Range: 0.1 to 10.0. If not set, fetch auto-scales depth based on the logo's character variance so flat logos don't look paper-thin.

```
height=36
```

Override the render height in rows (0 means auto; positive values are capped at 200 and constrained by the terminal). Default is auto (matches the number of info lines).

## Extra disks

Show additional mount points beyond the root filesystem:

```
disk=/home
disk=/data
```

Up to 8 extra mount points. Each one adds a line to the info output.

## Notes

- Lines starting with `#` are comments
- You don't need to remove the hint text in parentheses after values (e.g. `label_color=white (red, green, ...)`). The parser strips those automatically, except for `shading=`, `separator=`, and `disk=` which accept freeform strings
- CLI flags override config file settings
- If no config file exists, everything uses defaults

## Alignment

`v_alignment=top|center|bottom` and `h_alignment=left|center|right` control
placement. Padding is clamped to zero when the content exceeds the terminal.
