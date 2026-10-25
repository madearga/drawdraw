import json, os, sys, unittest, tempfile, pathlib, importlib.util

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class LicenseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.lic = load("license")
        self.lic.ENTITLEMENT = pathlib.Path(self.tmp.name) / "ent.json"
        self.lic.API_OVERRIDE = "mock"

    def tearDown(self):
        self.tmp.cleanup()

    def test_not_entitled_initially(self):
        self.assertFalse(self.lic.entitled())

    def test_activate_gumroad_mock(self):
        self.lic.cmd_activate(["KEY-123", "--provider", "gumroad", "--product", "pdt_x"])
        self.assertTrue(self.lic.entitled())
        ent = self.lic.read()
        self.assertEqual(ent["provider"], "gumroad")
        self.assertEqual(ent["product_id"], "pdt_x")

    def test_deactivate(self):
        self.lic.cmd_activate(["KEY-123", "--provider", "lemonsqueezy"])
        self.lic.cmd_deactivate([])
        self.assertFalse(self.lic.entitled())

    def test_activate_gumroad_requires_product(self):
        with self.assertRaises(SystemExit):
            self.lic.cmd_activate(["KEY-123", "--provider", "gumroad"])

    def test_mock_post_returns_success(self):
        status, payload = self.lic._post("https://example.invalid", {})
        self.assertEqual(status, 200)
        self.assertTrue(payload["success"])


class PaidGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = os.getcwd()
        os.chdir(self.tmp.name)
        self.pack = load("pack")
        self.lic = load("license")
        self.lic.API_OVERRIDE = "mock"
        self.pack.licensing = self.lic  # gate must read the test's entitlement
        self.pack.CHARACTERS = pathlib.Path("chars")
        self.pack.PACKS = pathlib.Path("chars/packs")
        self.pack.SETTINGS = pathlib.Path("settings.json")
        self.lic.ENTITLEMENT = pathlib.Path("ent.json")

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def make_paid_repo(self, version="1.0.0"):
        d = pathlib.Path("repo/packs/vip")
        d.mkdir(parents=True)
        (d / "character.md").write_text("# vip\n")
        (d / "reference.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (pathlib.Path("repo/index.json")).write_text(json.dumps({"packs": [{
            "name": "vip", "author": "t", "version": version,
            "description": "paid", "style": "riso", "aliases": [],
            "paid": True}]}))
        return d

    def test_paid_install_refused_without_license(self):
        with self.assertRaises(SystemExit) as cm:
            self.pack.cmd_install([str(self.make_paid_repo())])
        self.assertIn("paid pack", str(cm.exception))

    def test_paid_install_ok_with_license(self):
        self.lic.cmd_activate(["K", "--provider", "gumroad", "--product", "p"])
        self.pack.cmd_install([str(self.make_paid_repo())])
        self.assertTrue((self.pack.PACKS / "vip" / "character.md").exists())

    def test_paid_install_ok_with_dev_flag(self):
        self.pack.cmd_install([str(self.make_paid_repo()), "--dev"])
        self.assertTrue((self.pack.PACKS / "vip" / "character.md").exists())

    def test_free_pack_still_free(self):
        d = pathlib.Path("repo/packs/free")
        d.mkdir(parents=True)
        (d / "character.md").write_text("# free\n")
        (d / "reference.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (pathlib.Path("repo/index.json")).write_text(json.dumps({"packs": [{
            "name": "free", "author": "t", "version": "1.0.0",
            "description": "free", "style": "riso", "aliases": []}]}))
        self.pack.cmd_install([str(pathlib.Path("repo"))])
        self.assertTrue((self.pack.PACKS / "free" / "character.md").exists())


if __name__ == "__main__":
    unittest.main()
