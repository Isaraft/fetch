"""Color validation, formatting and configuration integration."""
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ColorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="ffetch-colors-")
        cls.work = Path(cls.temp.name)
        probe = cls.work / "probe.c"
        probe.write_text(
            '#define main fetch_original_main\n'
            f'#include "{ROOT / "fetch.c"}"\n'
            '#undef main\n'
            'int main(int argc, char **argv) {\n'
            ' if (argc == 4) {\n'
            '  char color[32] = "unchanged";\n'
            '  int ok = set_color(argv[1], color, (size_t)atoi(argv[3]), atoi(argv[2]));\n'
            '  printf("%d\\n%s", ok, color);\n'
            '  return 0;\n }\n'
            ' config_defaults();\n'
            ' if (!load_config(argc == 2 ? argv[1] : NULL)) return 1;\n'
            ' printf("%s\\n%s\\n%s", label_color, config_logo_outer, config_logo_inner);\n'
            ' return 0;\n}\n'
        )
        cls.binary = cls.work / "probe"
        subprocess.run(shlex.split(os.environ.get("CC", "cc"))
                       + shlex.split(os.environ.get("FFETCH_TEST_CFLAGS", "-O1 -g"))
                       + ['-DFETCH_CODENAME="test"', '-DFETCH_ARCH="test"', '-DFETCH_OS="test"',
                          str(probe), "-lm", "-o", str(cls.binary)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def parse(self, value, logo=False, capacity=32):
        result = subprocess.run([str(self.binary), value, str(int(logo)), str(capacity)],
                                capture_output=True, check=True, timeout=5)
        return result.stdout

    def test_rgb_boundaries_and_escape_bytes(self):
        for r, g, b in [(0, 0, 0), (255, 255, 255), (0, 255, 255), (57, 255, 20)]:
            params = f"38;2;{r};{g};{b}".encode()
            value = f"rgb:{r}:{g}:{b}"
            self.assertEqual(self.parse(value), b"1\n" + params)
            self.assertEqual(self.parse(value, logo=True), b"1\n\x1b[" + params + b"m")

    def test_named_and_numeric_ansi(self):
        for i, name in enumerate(["red", "green", "yellow", "blue", "magenta", "cyan", "white"], 31):
            self.assertEqual(self.parse(name), f"1\n{i}".encode())
            self.assertEqual(self.parse(str(i), logo=True), f"1\n\x1b[1;{i}m".encode())
        self.assertEqual(self.parse("97"), b"1\n97")

    def test_malformed_values_leave_destination_unchanged(self):
        invalid = ["", "rgb:", "rgb:0:255", "rgb:256:0:0", "rgb:-1:0:0",
                   "rgb:+1:2:3", "rgb:1:2:3extra", "rgb:1:2:3:4", "rgb:1::3",
                   "rgb:1:2:3 ", "rgb: 1:2:3", "rgb:1:2:3\x1b[2J",
                   "rgb:" + "9" * 200 + ":0:0", "unknown", "-1", "108", "36;2J"]
        for value in invalid:
            for logo in [False, True]:
                with self.subTest(value=value, logo=logo):
                    self.assertEqual(self.parse(value, logo), b"0\nunchanged")

    def test_small_buffer_is_rejected_without_mutation(self):
        for cap in [0, 1, 10, 19]:
            self.assertEqual(self.parse("rgb:255:255:255", True, cap), b"0\nunchanged")

    def test_invalid_config_preserves_previous_color(self):
        config = self.work / "config"
        config.write_text("label_color=cyan\nlabel_color=rgb:0:255:255garbage\n"
                          "logo_outer=rgb:0:255:255 (cyan)\nlogo_inner=red\n")
        result = subprocess.run([str(self.binary), str(config)], capture_output=True, check=True)
        self.assertEqual(result.stdout, b"36\n\x1b[38;2;0;255;255m\n\x1b[1;31m")
        self.assertIn(b"invalid label_color", result.stderr)

    def test_xdg_namespace_is_independent(self):
        home = self.work / "home"
        xdg = home / "settings"
        for name, value in [("fetch", "red"), ("ffetch-3d", "cyan")]:
            path = xdg / name / "config"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"label_color={value}\n")
        env = {**os.environ, "HOME": str(home), "XDG_CONFIG_HOME": str(xdg)}
        result = subprocess.run([str(self.binary)], env=env, capture_output=True, check=True)
        self.assertTrue(result.stdout.startswith(b"36\n"))

    def test_home_fallback_ignores_legacy_config(self):
        home = self.work / "fallback-home"
        for namespace, color in [("fetch", "red"), ("ffetch-3d", "cyan")]:
            path = home / ".config" / namespace / "config"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"label_color={color}\n")
        for relative_xdg in [None, "relative/settings"]:
            env = {**os.environ, "HOME": str(home)}
            env.pop("XDG_CONFIG_HOME", None)
            if relative_xdg is not None:
                env["XDG_CONFIG_HOME"] = relative_xdg
            result = subprocess.run([str(self.binary)], env=env, capture_output=True, check=True)
            self.assertTrue(result.stdout.startswith(b"36\n"))
        self.assertEqual((home / ".config/fetch/config").read_text(), "label_color=red\n")

    def test_missing_explicit_config_fails(self):
        result = subprocess.run([str(self.binary), str(self.work / "missing")], capture_output=True)
        self.assertEqual(result.returncode, 1)
