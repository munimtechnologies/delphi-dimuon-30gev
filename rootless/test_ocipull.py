# Tests for ocipull 0.1.0 (offline; no network). MV2 of Munim, Inc. Made with AI agents. Apache-2.0.
import io
import os
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import ocipull
except Exception as e:  # pragma: no cover
    ocipull = None
    _ERR = e


def _layer(entries):
    """entries: list of (kind, name, data_or_target). Returns a streaming tarfile."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        for kind, name, x in entries:
            ti = tarfile.TarInfo(name)
            if kind == "dir":
                ti.type, ti.mode = tarfile.DIRTYPE, 0o755
                tf.addfile(ti)
            elif kind == "file":
                b = x.encode()
                ti.size, ti.mode = len(b), 0o644
                tf.addfile(ti, io.BytesIO(b))
            elif kind == "sym":
                ti.type, ti.linkname = tarfile.SYMTYPE, x
                tf.addfile(ti)
            elif kind == "hard":
                ti.type, ti.linkname = tarfile.LNKTYPE, x
                tf.addfile(ti)
            elif kind == "fifo":
                ti.type = tarfile.FIFOTYPE
                tf.addfile(ti)
    buf.seek(0)
    return tarfile.open(fileobj=buf, mode="r|")


@unittest.skipIf(ocipull is None, "ocipull did not import")
class TestParse(unittest.TestCase):
    def test_ref(self):
        self.assertEqual(ocipull.parse_ref("gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd"),
                         ("gitlab-registry.cern.ch", "delphi/deployment/delphi/al9_64_xrd", "latest"))
        self.assertEqual(ocipull.parse_ref("reg.example:5000/a/b:v1"), ("reg.example:5000", "a/b", "v1"))
        self.assertEqual(ocipull.parse_ref("h/a/b@sha256:ab"), ("h", "a/b", "sha256:ab"))
        with self.assertRaises(ValueError):
            ocipull.parse_ref("justname")

    def test_www_authenticate(self):
        s, p = ocipull.parse_www_authenticate(
            'Bearer realm="https://gitlab.cern.ch/jwt/auth",service="container_registry",'
            'scope="repository:delphi/x:pull"')
        self.assertEqual(s, "bearer")
        self.assertEqual(p["realm"], "https://gitlab.cern.ch/jwt/auth")
        self.assertEqual(p["service"], "container_registry")
        self.assertEqual(p["scope"], "repository:delphi/x:pull")
        self.assertEqual(ocipull.parse_www_authenticate(""), (None, {}))

    def test_pick_platform(self):
        idx = {"manifests": [{"digest": "sha256:arm", "platform": {"architecture": "arm64", "os": "linux"}},
                             {"digest": "sha256:amd", "platform": {"architecture": "amd64", "os": "linux"}}]}
        self.assertEqual(ocipull.pick_platform(idx), "sha256:amd")
        with self.assertRaises(RuntimeError):
            ocipull.pick_platform({"manifests": []})


@unittest.skipIf(ocipull is None, "ocipull did not import")
@unittest.skipIf(os.name != "posix", "layer tests need POSIX symlinks (they run in the Linux job)")
class TestLayers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, "rootfs")
        self.outside = os.path.join(self.tmp.name, "outside")
        os.makedirs(self.root)
        os.makedirs(self.outside)

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, rel):
        with open(os.path.join(self.root, rel)) as f:
            return f.read()

    def test_resolve_stays_inside(self):
        os.makedirs(os.path.join(self.root, "usr/lib64"))
        os.symlink("usr/lib64", os.path.join(self.root, "lib64"))
        os.symlink(self.outside, os.path.join(self.root, "abs"))  # absolute link to a host path
        os.symlink("../../../..", os.path.join(self.root, "up"))
        r = ocipull.resolve_in_root(self.root, "lib64/libz.so")
        self.assertEqual(r, os.path.join(self.root, "usr", "lib64", "libz.so"))
        r = ocipull.resolve_in_root(self.root, "abs/x")
        self.assertTrue(r.startswith(self.root + os.sep), r)
        r = ocipull.resolve_in_root(self.root, "up/etc/passwd")
        self.assertEqual(r, os.path.join(self.root, "etc", "passwd"))
        r = ocipull.resolve_in_root(self.root, "../../etc/passwd")
        self.assertEqual(r, os.path.join(self.root, "etc", "passwd"))

    def test_symlink_loop(self):
        os.symlink("b", os.path.join(self.root, "a"))
        os.symlink("a", os.path.join(self.root, "b"))
        with self.assertRaises(OSError):
            ocipull.resolve_in_root(self.root, "a/x")

    def test_two_layers_with_whiteouts(self):
        st = ocipull.new_stats()
        ocipull.apply_layer(_layer([
            ("dir", "usr", None), ("dir", "usr/lib64", None),
            ("sym", "lib64", "usr/lib64"),
            ("file", "usr/lib64/libz.so", "z1"),
            ("dir", "etc", None), ("file", "etc/a", "A"), ("file", "etc/b", "B"),
            ("dir", "opt", None), ("file", "opt/old1", "o"), ("file", "opt/old2", "o"),
            ("hard", "usr/lib64/libz.so.1", "usr/lib64/libz.so"),
            ("fifo", "dev-fifo", None),
        ]), self.root, st)
        self.assertEqual(self.read("usr/lib64/libz.so.1"), "z1")
        self.assertEqual(st["skipped_dev"], 1)
        st2 = ocipull.new_stats()
        ocipull.apply_layer(_layer([
            ("file", "etc/.wh.a", ""),                 # delete etc/a
            ("file", "lib64/libnew.so", "n"),          # written through the lib64 symlink
            ("file", "usr/lib64/libz.so", "z2"),       # replace; the old hard link keeps z1
            ("sym", "etc/escape", self.outside),       # absolute link to a host path
            ("file", "etc/escape/evil", "x"),          # must land inside the root
            ("file", "../outside/evil2", "x"),         # '..' is clamped at the root
            ("file", "opt/.wh..wh..opq", ""),          # opaque: drop lower opt/*
            ("file", "opt/new", "N"),
        ]), self.root, st2)
        self.assertFalse(os.path.exists(os.path.join(self.root, "etc/a")))
        self.assertEqual(self.read("etc/b"), "B")
        self.assertEqual(self.read("usr/lib64/libnew.so"), "n")
        self.assertEqual(self.read("usr/lib64/libz.so"), "z2")
        self.assertEqual(self.read("usr/lib64/libz.so.1"), "z1")
        self.assertEqual(os.listdir(self.outside), [])  # nothing escaped
        self.assertEqual(sorted(os.listdir(os.path.join(self.root, "opt"))), ["new"])
        self.assertEqual(st2["whiteouts"], 1)
        self.assertEqual(st2["opaque"], 1)
        self.assertEqual(st2["errors"], 0)
        found = []
        for dp, dn, fn in os.walk(self.root):
            found += [f for f in fn if f.startswith("evil")]
        self.assertEqual(sorted(found), ["evil", "evil2"])

    def test_write_env(self):
        ocipull.write_env(self.root, {"config": {"Env": ["PATH=/usr/bin:/bin", "A=b c", "bad-key=1"]}})
        txt = self.read(".ocipull-env.sh")
        self.assertIn("export PATH=/usr/bin:/bin", txt)
        self.assertIn("export A='b c'", txt)
        self.assertNotIn("bad-key", txt)


if __name__ == "__main__":
    unittest.main()
