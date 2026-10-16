"""Terminal rendering, resize consistency, CLI precedence and staged installation."""
import fcntl
import os
from pathlib import Path
import pty
import re
import select
import signal
import struct
import subprocess
import tempfile
import termios
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "ffetch-3d"


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ffetch-runtime-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.config = self.home / "xdg/ffetch-3d/config"
        self.config.parent.mkdir(parents=True)
        self.config.write_text("custom_Test=RGB test\n")
        (self.config.parent / "logo.txt").write_text("  @  \n @@@ \n@@@@@\n")
        stubdir = self.home / "bin"
        stubdir.mkdir()
        stub = stubdir / "fastfetch"
        stub.write_text(f"#!{os.sys.executable}\nprint('\\033[31m  @  \\033[0m')\n"
                        "print('\\033[31m @@@ \\033[0m')\nprint('\\033[31m@@@@@\\033[0m')\n")
        stub.chmod(0o755)
        self.env = {**os.environ, "HOME": str(self.home), "XDG_CONFIG_HOME": str(self.home / "xdg"),
                    "TERM": "xterm-256color", "PATH": str(stubdir) + os.pathsep + os.environ["PATH"]}

    def render(self, args=(), dimensions=(50, 140), resize=None, binary=BIN):
        master, slave = pty.openpty()
        self.addCleanup(os.close, master)
        self.addCleanup(os.close, slave)
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", *dimensions, 0, 0))
        child = subprocess.Popen([str(binary), *args], stdin=slave, stdout=slave,
                                 stderr=subprocess.PIPE, env=self.env)
        data = b""
        changed = False
        deadline = time.monotonic() + 10
        try:
            while time.monotonic() < deadline:
                if select.select([master], [], [], 0.02)[0]:
                    data += os.read(master, 262144)
                if resize and not changed and b"\x1b[H" in data:
                    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", *resize, 0, 0))
                    child.send_signal(signal.SIGWINCH)
                    changed = True
                if child.poll() is not None:
                    while select.select([master], [], [], 0)[0]:
                        data += os.read(master, 262144)
                    break
            else:
                self.fail("renderer timed out")
        finally:
            if child.poll() is None:
                child.kill()
            _, errors = child.communicate(timeout=5)
        self.assertEqual(child.returncode, 0, errors.decode(errors="replace"))
        self.assertNotIn(b"runtime error:", errors)
        self.assertNotIn(b"AddressSanitizer", errors)
        # Remove terminal setup/cleanup and retain complete frame payloads.
        frames = data.split(b"\x1b[H")[1:]
        frames = [re.split(rb"\x1b\[\?(?:25|1002|1006)[hl]", frame)[0]
                  .replace(b"\x1b[2J", b"") for frame in frames]
        return frames, data

    def test_all_rendering_modes_emit_synchronized_truecolor(self):
        for mode in ["ascii", "blocks", "sextants"]:
            with self.subTest(mode=mode):
                _, data = self.render(["--frames", "2", "--color", "rgb:0:255:255",
                                       "--shading-mode", mode])
                self.assertIn(b"\x1b[38;2;0;255;255m", data)
                self.assertIn(b"\x1b[1;38;2;0;255;255m", data)
                self.assertNotIn(b"\\033[", data)
                self.assertNotIn(b"\x00", data)

    def test_embedded_colors_are_used_only_without_an_override(self):
        _, default = self.render(["--frames", "1", "--no-info", "--logo", "test"])
        _, custom = self.render(["--frames", "1", "--no-info", "--logo", "test",
                                 "--color", "rgb:1:2:3"])
        self.assertIn(b"\x1b[1;31m", default)
        self.assertNotIn(b"\x1b[1;31m", custom)
        self.assertIn(b"\x1b[38;2;1;2;3m", custom)

    def test_cli_geometry_overrides_config(self):
        args = ["--frames", "3", "--no-info", "--size", "1.5", "--height", "45",
                "--depth", "1.5", "--speed", "1", "--rotate-y", "--shading-mode", "blocks"]
        reference, _ = self.render(args)
        self.config.write_text("size=0.5\nheight=20\ndepth=0.1\nspeed=3\nspin=x\nshading=AB\n")
        configured, _ = self.render(args)
        self.assertEqual(configured, reference)

    def test_resize_matches_fresh_projection_in_both_directions(self):
        for dims, target in [((50, 140), (28, 75)), ((28, 75), (50, 140)),
                             ((50, 140), (15, 35))]:
            for height in [[], ["--height", "45"]]:
                with self.subTest(dimensions=dims, target=target, height=height):
                    args = ["--frames", "8", "--speed", "0", "--size", "1.5",
                            "--shading-mode", "blocks", *height]
                    fresh, _ = self.render(args, target)
                    resized, _ = self.render(args, dims, target)
                    self.assertEqual(resized[-1], fresh[-1])

    def test_later_color_options_override_launcher_defaults(self):
        self.env["FFETCH_3D_BIN"] = str(BIN)
        _, data = self.render(["--frames", "1", "--logo", "arch", "--color", "rgb:1:2:3",
                               "--label-color", "cyan"], binary=ROOT / "scripts/arcticfetch")
        self.assertIn(b"\x1b[38;2;1;2;3m", data)
        self.assertIn(b"\x1b[1;36m", data)

    def test_malformed_cli_is_rejected(self):
        cases = [["--color", "rgb:1:2:3bad"], ["--size", "nan"], ["--depth", "inf"],
                 ["--height", "-1"], ["--frames", "99999999999999999"],
                 ["--speed", "1oops"], ["--config"], ["--logo-outer"]]
        for args in cases:
            with self.subTest(args=args):
                result = subprocess.run([str(BIN), *args], env=self.env, capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 1)
                self.assertIn(b"ffetch-3d:", result.stderr)

    def test_staged_install_uses_separate_names(self):
        stage = self.home / "stage with spaces"
        subprocess.run(["make", "install", f"DESTDIR={stage}", "PREFIX=/usr"], cwd=ROOT,
                       check=True, capture_output=True)
        bindir = stage / "usr/bin"
        self.assertEqual({p.name for p in bindir.iterdir()},
                         {"ffetch-3d", "ffetch-neon", "ffetch-arctic"})
        self.assertTrue((stage / "usr/share/doc/ffetch-3d/LICENSE").is_file())
        self.env.pop("FFETCH_3D_BIN", None)
        _, data = self.render(["--frames", "1"], binary=bindir / "ffetch-arctic")
        self.assertIn(b"\x1b[38;2;0;255;255m", data)
