# Changelog

## Unreleased

### Security

- Remove shell interpretation from the inherited Fastfetch logo-loading path.
  Logo names are passed as a single process argument. Add regression coverage
  for literal argument handling and an unavailable Fastfetch executable.
  The renderer and logo-loading feature originate in areofyl/fetch.
