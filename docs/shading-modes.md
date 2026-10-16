# Shading modes

FFetch-3D supports three shading modes for the 3D rendering. ASCII is the default.

## ASCII (default)

Brightness is mapped onto the character ramp `.,-~:;=!*#$@`, one character per cell. This is the classic donut.c look.

```
ffetch-3d --shading-mode ascii
```

![ascii](shading-ascii.png)

## Blocks

Coverage is sampled on a 2x2 grid per cell, using Unicode quadrant blocks (`▘▝▀▖▌▞▛▗▚▐▜▄▙▟█`). Edges land on half-cell boundaries instead of snapping to the character grid.

Requires a UTF-8 locale and quadrant-block glyph support in the terminal/font.

```
ffetch-3d --shading-mode blocks
```

![blocks](shading-blocks.png)

## Sextants

Coverage is sampled on a 2x3 grid per cell, using Unicode block sextants (U+1FB00). This gives the sharpest edges.

Requires terminal/font support for the Symbols for Legacy Computing block (U+1FB00).

```
ffetch-3d --shading-mode sextants
```

![sextants](shading-sextants.png)

## Config

Set the mode in `~/.config/ffetch-3d/config`:

```
shading_mode=ascii
```

Or use a custom ASCII ramp:

```
shading=.,-~:;=!*#$@
```

Setting `shading=` implies ASCII mode. `--shading-chars` on the CLI does the same.
