import os, sys, unittest, tempfile, pathlib, json, importlib.util

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class PackTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = os.getcwd()
        os.chdir(self.tmp.name)
        self.pack = load("pack")
        self.pack.CHARACTERS = pathlib.Path("chars")
        self.pack.PACKS = pathlib.Path("chars/packs")
        self.pack.SETTINGS = pathlib.Path("settings.json")

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def pack_files(self, d):
        d.mkdir(parents=True, exist_ok=True)
        (d / "character.md").write_text("# pack\n\ntest\n")
        (d / "reference.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")

    def meta(self, name, aliases=None, version="1.0.0"):
        return {"name": name, "author": "t", "version": version,
                "description": "test", "style": "riso", "aliases": aliases or []}

    def builtin_klik(self):
        d = self.pack.CHARACTERS / "klik"
        self.pack_files(d)
        (self.pack.CHARACTERS / "index.json").write_text(json.dumps(
            {"packs": [self.meta("klik", aliases=["cursor", "pointer"])]}))

    def test_resolve_builtin_by_alias_and_default(self):
        self.builtin_klik()
        meta, d = self.pack.resolve("cursor")
        self.assertEqual(meta["name"], "klik")
        meta, _ = self.pack.resolve(None)
        self.assertEqual(meta["name"], "klik")

    def test_install_repo_with_packs_folder(self):
        root = pathlib.Path("repo")
        self.pack_files(root / "packs" / "one")
        self.pack_files(root / "packs" / "two")
        (root / "index.json").write_text(json.dumps(
            {"packs": [self.meta("one"), self.meta("two")]}))
        self.pack.cmd_install([str(root)])
        names = {m["name"] for m, _ in self.pack.all_packs()}
        self.assertIn("one", names)
        self.assertIn("two", names)
        self.assertTrue((self.pack.PACKS / "two" / "reference.png").exists())

    def test_install_bare_pack_with_parent_index(self):
        (pathlib.Path("repo/packs/bugsi")).mkdir(parents=True)
        self.pack_files(pathlib.Path("repo/packs/bugsi"))
        (pathlib.Path("repo/index.json")).write_text(json.dumps(
            {"packs": [self.meta("bugsi", aliases=["bug"])]}))
        self.pack.cmd_install([str(pathlib.Path("repo/packs/bugsi"))])
        meta, d = self.pack.resolve("bug")
        self.assertEqual(meta["name"], "bugsi")
        self.assertTrue((d / "reference.png").exists())

    def test_install_self_listing_pack(self):
        d = pathlib.Path("single/bugsi")
        self.pack_files(d)
        (d / "index.json").write_text(json.dumps({"packs": [self.meta("bugsi")]}))
        self.pack.cmd_install([str(d)])
        meta, _ = self.pack.resolve("bugsi")
        self.assertEqual(meta["name"], "bugsi")

    def test_default_roundtrip(self):
        d = pathlib.Path("single/bugsi")
        self.pack_files(d)
        (d / "index.json").write_text(json.dumps({"packs": [self.meta("bugsi")]}))
        self.pack.cmd_install([str(d)])
        self.pack.cmd_default(["bugsi"])
        self.assertEqual(self.pack.read_default(), "bugsi")
        meta, _ = self.pack.resolve(None)
        self.assertEqual(meta["name"], "bugsi")

    def test_install_rejects_incomplete_pack(self):
        bad = pathlib.Path("repo/packs/nope")
        bad.mkdir(parents=True)
        (bad / "character.md").write_text("x")  # no reference.png
        (pathlib.Path("repo/index.json")).write_text(json.dumps({"packs": [self.meta("nope")]}))
        with self.assertRaises(SystemExit):
            self.pack.cmd_install([str(pathlib.Path("repo/packs/nope"))])

    def test_install_rejects_unknown_dir(self):
        empty = pathlib.Path("empty")
        empty.mkdir()
        with self.assertRaises(SystemExit):
            self.pack.cmd_install([str(empty)])

    def test_reinstall_replaces(self):
        d = pathlib.Path("single/bugsi")
        self.pack_files(d)
        (d / "index.json").write_text(json.dumps({"packs": [self.meta("bugsi", version="1.0.0")]}))
        self.pack.cmd_install([str(d)])
        (d / "index.json").write_text(json.dumps({"packs": [self.meta("bugsi", version="1.1.0")]}))
        self.pack.cmd_install([str(d)])
        metas = [m for m, _ in self.pack.all_packs() if m["name"] == "bugsi"]
        self.assertEqual(len(metas), 1)
        self.assertEqual(metas[0]["version"], "1.1.0")


if __name__ == "__main__":
    unittest.main()
