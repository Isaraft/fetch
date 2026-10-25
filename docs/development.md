# Development and validation

FFetch-3D starts from upstream commit `7b19d22` (fetch 2.3.0), followed by a
baseline commit preserving the working local RGB customization and launchers.
The checkout is independent of the original AUR cache; Git objects are not
shared through alternates. The `upstream` remote tracks areofyl/fetch.
The `origin` remote points to [Isaraft/fetch](https://github.com/Isaraft/fetch).
The initial publication merges later upstream bounds checks and regression
tests without rewriting either history. Upstream pushes remain disabled.
Development used AI assistance, with local compilation and regression validation.

## Local checks

```sh
make
make test
bash -n scripts/neonfetch scripts/arcticfetch
git diff --check
```

The upstream C unit tests and POSIX regressions run alongside the fork tests.
Python tests use temporary directories, a fake Fastfetch, and POSIX pseudo
terminals. They do not use a real user's config. Runtime tests compare frames
after a resize with fresh frames at the target dimensions, with stationary
rotation for deterministic comparison. Other tests exercise animated frames.

The security regression checks literal subprocess arguments using inert names;
it contains no executable exploit payload. RGB tests compile a small harness
against the same C source so they can check buffer capacity and unchanged values
on rejection. Launcher tests run simultaneous processes and compare all files
before and after execution.

To run AddressSanitizer and UndefinedBehaviorSanitizer:

```sh
make -B ffetch-3d tests/shared CFLAGS='-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer'
ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 \
FFETCH_TEST_CFLAGS='-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer' \
make test
make -B ffetch-3d tests/shared
```

Leak detection is disabled in that example for environments where LeakSanitizer
cannot run. This does not constitute a leak check. A regular build should be
restored before using a development executable interactively.

## Layout invariants

- Keep `fixed_y_center + 2.0f` as the approved vertical placement.
- Recompute projection scale and center from current layout on resize.
- Use identical configuration and CLI precedence at startup and after resize.
- Budget the vertical offset during automatic face-on height tightening.
- Keep RGB palette selection independent for each process.

A bounded frame test is not a visual approval of every rotation, terminal,
font, or extreme size. Manually inspect enlarged Arch logos in Konsole before
changing the projection aesthetic. Avoid silently installing or adding shell
startup commands during development.

## Release status and limitations

This is an unreleased development version. Linux x86_64 is validated locally;
macOS, other architectures, and the Nix package are not yet tested. Inherited
compiler warnings remain, predominantly around formatting, truncation, and
unused parameters. The projection fits the face-on logo rather than every
rotated extent, so extreme sizes and depth can still clip.

Inherited legacy package recipes are retained separately for reference rather
than presented as supported installers. A future release needs updated
repository URLs and maintainer metadata before those recipes can be activated.
