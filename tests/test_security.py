"""Ensure the logo subprocess receives literal argv, without executable payloads."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LogoProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="ffetch-security-")
        cls.work = Path(cls.temp.name)
        probe = cls.work / "probe.c"
        probe.write_text(
            '#define main fetch_original_main\n'
            f'#include "{ROOT / "fetch.c"}"\n'
            '#undef main\n'
            'int main(int argc, char **argv) {\n'
            '  return argc != 2 || !load_logo_ff_colored(argv[1]);\n}\n'
        )
        cls.binary = cls.work / "probe"
        subprocess.run(
            shlex.split(os.environ.get("CC", "cc"))
            + shlex.split(os.environ.get("FFETCH_TEST_CFLAGS", "-O1 -g"))
            + ['-DFETCH_CODENAME="test"', '-DFETCH_ARCH="test"', '-DFETCH_OS="test"',
               str(probe), "-lm", "-o", str(cls.binary)], check=True,
        )
        cls.log = cls.work / "arguments.json"
        stub = cls.work / "fastfetch"
        stub.write_text(
            f"#!{os.sys.executable}\n"
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "Path(os.environ['FFETCH_ARG_LOG']).write_text(json.dumps(sys.argv[1:]))\n"
            "print('  @@@  ')\nprint(' @@@@@ ')\n"
        )
        stub.chmod(0o755)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_literal_logo_argument(self):
        # Inert punctuation catches shell splitting without publishing an exploit.
        for name in ["arch", "logo with spaces", "punctuation; [brackets] 'quotes' &",
                     "double\"quote", "long-" + "x" * 1024]:
            with self.subTest(name=name):
                env = {**os.environ, "PATH": str(self.work), "FFETCH_ARG_LOG": str(self.log)}
                subprocess.run([str(self.binary), name], env=env, check=True,
                               capture_output=True, timeout=5)
                self.assertEqual(json.loads(self.log.read_text()),
                                 ["-c", "none", "-l", name, "-s", "break", "--pipe", "false"])

    def test_missing_fastfetch_is_handled(self):
        empty = self.work / "empty"
        empty.mkdir(exist_ok=True)
        result = subprocess.run([str(self.binary), "arch"],
                                env={**os.environ, "PATH": str(empty)},
                                capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 1)
