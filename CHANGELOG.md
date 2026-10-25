# Changelog

## Unreleased

### Added

- Per-process color options, explicit config selection, and the original
  twelve-color neon palette without configuration writes.
- Dedicated `ffetch-3d`, `ffetch-neon`, and `ffetch-arctic` installation names
  and an independent XDG configuration directory.
- Automated RGB validation and concurrent launcher tests.
- English documentation, a cyan rendering preview, and development notes.
- Preserve inactive upstream package recipes separately; adapt Nix names
  without claiming untested packaging support.

### Fixed

- Merge upstream buffer bounds and minimal-logo fixes, retaining their tests.
- Accept zero and reverse config speeds with bounded numeric validation.

- Strict RGB validation, bounded escape formatting, and numeric argument checks.
- Forward launcher arguments and consistently prioritize CLI settings.
- Preserve embedded logo colors when no surface override is configured.
- Recompute scale and projection center together on terminal resize, retaining
  the approved two-row offset and budgeting for it during automatic sizing.
- Clamp alignment padding and account for stacked information layouts.
- Emit line-clear sequences without an unintended terminating NUL byte.

### Security

- Remove shell interpretation from the inherited Fastfetch logo-loading path.
  Logo names are passed as a single process argument. Add regression coverage
  for literal argument handling and an unavailable Fastfetch executable.
  The renderer and logo-loading feature originate in areofyl/fetch.
