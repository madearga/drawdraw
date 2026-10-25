import os, sys, unittest, tempfile, pathlib, importlib.util

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CutoutTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = os.getcwd()
        os.chdir(self.tmp.name)

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_chroma_removed_interior_survives(self):
        from pnglib import write_png, decode_png
        cut = load("cutout")
        # magenta field with a red square that CONTAINS a magenta dot:
        # the border flood must stop at the red square, so the inner
        # magenta dot survives.
        size = 64
        rows = [[(255, 0, 255, 255)] * size for _ in range(size)]
        for y in range(24, 40):
            for x in range(24, 40):
                rows[y][x] = (200, 0, 0, 255)
        rows[31][32] = (255, 0, 255, 255)  # inner magenta dot
        write_png("in.png", size, size, rows)
        out = cut.cutout(rows, (255, 0, 255), 90)
        self.assertEqual(out[0][0], (255, 0, 255, 0))          # border removed
        self.assertEqual(out[30][30], (200, 0, 0, 255))        # subject intact
        self.assertEqual(out[31][32][3], 255)                  # inner dot survives

    def test_cli_roundtrip(self):
        import subprocess
        from pnglib import write_png, decode_png
        cut = load("cutout")
        size = 32
        rows = [[(255, 0, 255, 255)] * size for _ in range(size)]
        for y in range(12, 20):
            for x in range(12, 20):
                rows[y][x] = (0, 128, 0, 255)
        write_png("in.png", size, size, rows)
        r = subprocess.run([sys.executable, str(SCRIPTS / "cutout.py"),
                            "in.png", "out.png"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        _, _, out = decode_png("out.png")
        self.assertEqual(out[0][0][3], 0)
        self.assertEqual(out[15][15][3], 255)


class DoctorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def run_doctor(self, env=None):
        import subprocess
        e = dict(os.environ)
        for k in ("GEMINI_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY",
                  "GROK_HOME"):
            e.pop(k, None)
        # hermetic HOME: hide the real ~/.pi and ~/.grok
        e["HOME"] = self.tmp.name
        if env:
            e.update(env)
        return subprocess.run([sys.executable, str(SCRIPTS / "doctor.py")],
                              capture_output=True, text=True, env=e)

    def test_exit_zero_when_a_key_engine_exists(self):
        r = self.run_doctor(env={"GEMINI_API_KEY": "x"})
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("default engine: gemini", r.stdout)

    def test_exit_one_when_nothing_usable(self):
        r = self.run_doctor()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("no engine usable", r.stdout)

    def test_codex_line_printed(self):
        r = self.run_doctor(env={"OPENAI_API_KEY": "x"})
        self.assertIn("codex:", r.stdout)
        self.assertIn("grok:", r.stdout)


if __name__ == "__main__":
    unittest.main()
