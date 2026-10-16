"""Argument forwarding and simultaneous launchers must not write configuration."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PALETTE = {"255:0:255", "0:255:255", "57:255:20", "191:0:255", "255:20:147",
           "0:128:255", "255:95:0", "204:255:0", "255:23:68", "143:0:255",
           "0:255:200", "255:214:0"}


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ffetch-launchers-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.stub = self.home / "argument recorder"
        self.stub.write_text(f"#!{os.sys.executable}\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n")
        self.stub.chmod(0o755)
        self.env = {**os.environ, "HOME": str(self.home), "XDG_CONFIG_HOME": str(self.home / "xdg"),
                    "FFETCH_3D_BIN": str(self.stub)}

    def run_launcher(self, name, *args):
        result = subprocess.run([str(ROOT / "scripts" / name), *args], env=self.env,
                                capture_output=True, check=True, text=True, timeout=5)
        return json.loads(result.stdout)

    def test_arguments_remain_separate_and_ordered(self):
        extra = ["--size", "1.5", "--config", "path with spaces", "--color", "rgb:1:2:3"]
        for name in ["neonfetch", "arcticfetch"]:
            args = self.run_launcher(name, *extra)
            self.assertEqual(args[:4], ["-l", "arch", "--shading-mode", "blocks"])
            self.assertEqual(args[6:], extra)

    def test_fixed_cyan(self):
        self.assertEqual(self.run_launcher("arcticfetch")[4:], ["--color", "rgb:0:255:255"])

    def test_palette_is_exact(self):
        # Check all choices, rather than a flaky expectation of random coverage.
        import re
        choices = re.findall(r'^  "([0-9]+:[0-9]+:[0-9]+)"',
                             (ROOT / "scripts/neonfetch").read_text(), re.M)
        self.assertEqual(len(choices), 12)
        self.assertEqual(set(choices), PALETTE)
        self.assertIn(self.run_launcher("neonfetch")[5].removeprefix("rgb:"), PALETTE)

    def test_concurrent_launches_do_not_change_shared_files(self):
        configs = [self.home / ".config/fetch/config", self.home / "xdg/ffetch-3d/config"]
        for config in configs:
            config.parent.mkdir(parents=True)
            config.write_bytes(b"keep this configuration exactly\n")
        before = {str(p.relative_to(self.home)): p.read_bytes()
                  for p in self.home.rglob("*") if p.is_file()}
        with ThreadPoolExecutor(max_workers=8) as pool:
            args = list(pool.map(lambda i: self.run_launcher("neonfetch" if i % 2 else "arcticfetch"),
                                 range(32)))
        for argv in args:
            self.assertIn(argv[5].removeprefix("rgb:"), PALETTE)
        after = {str(p.relative_to(self.home)): p.read_bytes()
                 for p in self.home.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_launch_does_not_create_a_config(self):
        self.run_launcher("neonfetch")
        self.assertFalse((self.home / ".config").exists())
        self.assertFalse((self.home / "xdg").exists())
