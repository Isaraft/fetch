# Nix and Home Manager

These adapted recipes have not yet been validated with Nix. See
[packaging status](../packaging/README.md). The original Nix implementation
is retained in upstream history.

For a local flake checkout:

```sh
nix build .
./result/bin/ffetch-3d --help
./result/bin/ffetch-neon --frames 60
```

In a Home Manager flake, import this checkout's
`homeManagerModules.default`. The namespace is `programs.ffetch-3d`:

```nix
programs.ffetch-3d = {
  enable = true;
  labelColor = "rgb:0:255:255";
  info = [ "os" "kernel" "uptime" ];
  speed = 1.0;
  spin = "xy";
  extraConfig = ''
    shading_mode=blocks
    logo_outer=rgb:0:255:255
    logo_inner=rgb:0:255:255
  '';
};
```

The module writes `ffetch-3d/config` under the XDG config directory. It
exposes `info`, `labelColor`, `separator`, `shading`, `light`, `spin`, `speed`,
`size`, `height`, and `extraConfig`. Other settings can go in `extraConfig`.
No GitHub owner or release URL is assumed for the fork.
