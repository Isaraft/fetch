# Packaging

The supported local installation path is `make install PREFIX=...`, with
optional `DESTDIR` staging. It installs `ffetch-3d`, `ffetch-neon`, and
`ffetch-arctic`; it does not install a command named `fetch` or edit user config.

The Nix recipe and Home Manager module in `../nix` have been adjusted to the
fork's names. They remain untested because Nix is not available in the local
validation environment. Test them before using them for distribution.

`upstream/` retains the original Debian, RPM, and Open Build Service metadata
for provenance and future adaptation. These are inactive reference files,
not FFetch-3D installers. They still contain upstream names, URLs, authors, and
historical release data. Do not build or publish them as FFetch-3D packages.
New recipes need the final repository URL, maintainer details, fork names,
and packaging-system validation before activation.
