import os, sys, unittest, tempfile, pathlib, importlib.util

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class PngTest(unittest.TestCase):
    def test_roundtrip(self):
        from pnglib import encode_png, decode_png
        import tempfile, os
        rows = [[(255, 0, 0, 255) * 4 for _ in range(4)] for _ in range(4)]
        rows[0][0] = (0, 255, 0, 255)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(encode_png(4, 4, rows))
            path = f.name
        w, h, out = decode_png(path)
        os.unlink(path)
        self.assertEqual((w, h), (4, 4))
        self.assertEqual(out[0][0], (0, 255, 0, 255))
        self.assertEqual(out[3][3], (255, 0, 0, 255))

    def test_filters(self):
        # Re-encode with all filter types via zlib raw paths: craft a PNG
        # with filter 1 (sub) manually and check decode.
        import struct, zlib, tempfile, os
        w = h = 2
        raw = b"\x01" + b"\xff\x00\x00" * 2 + b"\x01" + b"\x00\xff\x00" * 2
        ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
        def chunk(tag, data):
            return struct.pack(">I", len(data)) + tag + data + struct.pack(
                ">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
               + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png)
            path = f.name
        _, _, rows = load("pnglib").decode_png(path)
        os.unlink(path)
        self.assertEqual(rows[1][1], (0, 254, 0, 255))  # sub wraps mod 256


class OnModelTest(unittest.TestCase):
    def test_identical_is_one(self):
        om = load("onmodel")
        ref = SCRIPTS.parent / "characters" / "klik" / "reference.png"
        self.assertGreater(om.score(ref, ref), 0.99)

    def test_different_scores_lower(self):
        om = load("onmodel")
        ref = SCRIPTS.parent / "characters" / "klik" / "reference.png"
        import tempfile
        sys.path.insert(0, str(SCRIPTS))
        from pnglib import write_png
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "other.png"
            # vertical stripes vs the cursor: very different structure
            rows = [[(255, 255, 255, 255) if (x // 4) % 2 else (0, 0, 0, 255)
                     for x in range(256)] for y in range(256)]
            write_png(p, 256, 256, rows)
            s_stripe = om.score(ref, p)
            s_same = om.score(ref, ref)
            self.assertLess(s_stripe, s_same)


class SpecTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = pathlib.Path.cwd()
        os.chdir(self.tmp.name)

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def run_spec(self, *args):
        import subprocess
        return subprocess.run([sys.executable, str(SCRIPTS / "spec.py"), *args],
                              capture_output=True, text=True)

    def test_init_next_set_list(self):
        brief = pathlib.Path("brief.md")
        brief.write_text("- deploy day\n- incident night\n")
        r = self.run_spec("init", "--character", "klik", "--brief", "brief.md")
        self.assertIn("2 shot(s)", r.stdout, r.stderr)
        r = self.run_spec("next")
        self.assertTrue(r.stdout.startswith("s01\tdeploy day"))
        r = self.run_spec("set", "s01", "pass", "0.71")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.run_spec("next")
        self.assertTrue(r.stdout.startswith("s02\tincident night"))
        r = self.run_spec("list")
        self.assertIn("pass\t0.71", r.stdout)
        self.assertIn("deploy day", r.stdout)

    def test_set_rejects_bad_status(self):
        self.run_spec("init", "--scenes", "one")
        r = self.run_spec("set", "s01", "bogus")
        self.assertNotEqual(r.returncode, 0)


class GateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = pathlib.Path.cwd()
        os.chdir(self.tmp.name)

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def build_run(self):
        import json
        b = pathlib.Path("illo-build")
        (b / "shots").mkdir(parents=True)
        (b / "prompts").mkdir()
        (b / "spec.json").write_text(json.dumps({"character": "klik", "min_score": 0.55}))
        return b

    def write_png_at(self, path, size=600):
        from pnglib import write_png
        rows = [[(200, 200, 200, 255)] * size for _ in range(size)]
        write_png(path, size, size, rows)

    def run_gate(self):
        import subprocess
        return subprocess.run([sys.executable, str(SCRIPTS / "gate.py")],
                              capture_output=True, text=True)

    def test_passes_when_all_pass(self):
        b = self.build_run()
        self.write_png_at(b / "shots" / "s01.png")
        (b / "shots.csv").write_text(
            "id,concept,palette,status,file,score,tries\n"
            "s01,test,default,pass,shots/s01.png,0.80,1\n")
        r = self.run_gate()
        self.assertIn("GATE PASSED", r.stdout, r.stderr)
        self.assertEqual(r.returncode, 0)

    def test_fails_on_pending(self):
        b = self.build_run()
        self.write_png_at(b / "shots" / "s01.png")
        (b / "shots.csv").write_text(
            "id,concept,palette,status,file,score,tries\n"
            "s01,test,default,pending,shots/s01.png,,0\n")
        r = self.run_gate()
        self.assertIn("GATE FAILED", r.stdout)
        self.assertEqual(r.returncode, 1)

    def test_fails_on_low_score(self):
        b = self.build_run()
        self.write_png_at(b / "shots" / "s01.png")
        (b / "shots.csv").write_text(
            "id,concept,palette,status,file,score,tries\n"
            "s01,test,default,pass,shots/s01.png,0.30,1\n")
        r = self.run_gate()
        self.assertIn("score 0.30 < 0.55", r.stdout)
        self.assertEqual(r.returncode, 1)

    def test_fails_on_missing_file(self):
        b = self.build_run()
        (b / "shots.csv").write_text(
            "id,concept,palette,status,file,score,tries\n"
            "s01,test,default,pass,shots/s01.png,0.80,1\n")
        r = self.run_gate()
        self.assertIn("missing", r.stdout)
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
