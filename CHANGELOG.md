# Changelog

## Unreleased

### Added

- Per-process color options, explicit config selection, and the original
  twelve-color neon palette without configuration writes.
- Dedicated `ffetch-3d`, `ffetch-neon`, and `ffetch-arctic` installation names
  and an independent XDG configuration directory.
- Automated RGB validation and concurrent launcher tests.

### Fixed

- Strict RGB validation, bounded escape formatting, and numeric argument checks.
- Forward launcher arguments and consistently prioritize CLI settings.
- Preserve embedded logo colors when no surface override is configured.

### Security

- Remove shell interpretation from the inherited Fastfetch logo-loading path.
  Logo names are passed as a single process argument. Add regression coverage
  for literal argument handling and an unavailable Fastfetch executable.
  The renderer and logo-loading feature originate in areofyl/fetch.
