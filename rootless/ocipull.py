#!/usr/bin/env python3
"""ocipull 0.1.0 -- pull a public OCI / Docker image into a plain directory (a root
file system) without docker, so that the DELPHI open-data software container
(gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd) can be run rootless
under proot inside an ordinary python:3.12 job.

Part of the open, pre-registered DELPHI test of the ALEPH 30 GeV dimuon excess
(https://github.com/munimtechnologies/delphi-dimuon-30gev, amendment 0.33).
MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.

Standard library only (zstd layers need the optional 'zstandard' package).
Every blob is checked against its sha256 digest. Layers are applied in order with
OCI whiteouts; every path, symlink and hard link is resolved INSIDE the root, so a
layer can never write outside it. Ownership is not restored (proot runs as the
job's user); device nodes and fifos are skipped.

Usage:
  python3 ocipull.py IMAGE --rootfs DIR --blobs DIR --summary FILE.json
"""
import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import stat
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "0.1.0"
UA = "ocipull/0.1 (open-data research client)"
ACCEPT_MANIFEST = ", ".join([
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
])
STAMP = ".ocipull-complete"


# ----------------------------------------------------------------------------- parsing
def parse_ref(ref):
    """'host/path/name[:tag|@sha256:...]' -> (host, repo, tag_or_digest)."""
    host, _, rest = ref.partition("/")
    if not rest:
        raise ValueError("image reference needs a registry host: %r" % ref)
    if "@" in rest:
        repo, _, tag = rest.partition("@")
        return host, repo, tag
    i = rest.rfind(":")
    if i != -1 and i > rest.rfind("/"):
        return host, rest[:i], rest[i + 1:]
    return host, rest, "latest"


def parse_www_authenticate(h):
    """'Bearer realm="...",service="..."' -> ('bearer', {'realm': ..., 'service': ...})."""
    m = re.match(r"\s*(\w+)\s+(.*)", h or "")
    if not m:
        return None, {}
    return m.group(1).lower(), dict(re.findall(r'(\w+)="([^"]*)"', m.group(2)))


def pick_platform(index, arch="amd64", os_name="linux"):
    for d in index.get("manifests", []):
        p = d.get("platform", {})
        if p.get("architecture") == arch and p.get("os") == os_name:
            return d["digest"]
    raise RuntimeError("no %s/%s manifest in index: %s" % (
        os_name, arch, [d.get("platform") for d in index.get("manifests", [])]))


# ----------------------------------------------------------------------------- registry
class _StripAuthRedirect(urllib.request.HTTPRedirectHandler):
    """Drop the registry token when a blob redirects to another host (object storage)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and (urllib.parse.urlsplit(newurl).netloc
                                != urllib.parse.urlsplit(req.full_url).netloc):
            for k in list(new.headers):
                if k.lower() == "authorization":
                    del new.headers[k]
            for k in list(new.unredirected_hdrs):
                if k.lower() == "authorization":
                    del new.unredirected_hdrs[k]
        return new


OPENER = urllib.request.build_opener(_StripAuthRedirect)


class Registry:
    def __init__(self, host, repo):
        self.host, self.repo, self.token = host, repo, None

    def _auth(self, hdr):
        scheme, p = parse_www_authenticate(hdr)
        if scheme != "bearer" or "realm" not in p:
            raise RuntimeError("unsupported registry auth: %r" % hdr)
        q = {"service": p.get("service", ""),
             "scope": p.get("scope") or "repository:%s:pull" % self.repo}
        url = p["realm"] + "?" + urllib.parse.urlencode(q)
        with OPENER.open(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
            j = json.load(r)
        self.token = j.get("token") or j.get("access_token")
        if not self.token:
            raise RuntimeError("registry returned no token")

    def open(self, path, accept=None, _retry=True):
        url = "https://%s/v2/%s/%s" % (self.host, self.repo, path)
        h = {"User-Agent": UA}
        if accept:
            h["Accept"] = accept
        if self.token:
            h["Authorization"] = "Bearer " + self.token
        try:
            return OPENER.open(urllib.request.Request(url, headers=h), timeout=120)
        except urllib.error.HTTPError as e:
            if e.code == 401 and _retry:
                self._auth(e.headers.get("WWW-Authenticate", ""))
                return self.open(path, accept, _retry=False)
            raise

    def manifest(self, ref, arch="amd64", os_name="linux", _depth=0):
        with self.open("manifests/" + ref, ACCEPT_MANIFEST) as r:
            m = json.load(r)
            digest = r.headers.get("Docker-Content-Digest", "")
        if "manifests" in m:
            if _depth > 2:
                raise RuntimeError("nested image index")
            return self.manifest(pick_platform(m, arch, os_name), arch, os_name, _depth + 1)
        return m, digest or ref

    def blob(self, digest, dest):
        want = digest.split(":", 1)[1]
        if os.path.exists(dest) and sha256_file(dest) == want:
            return "cached"
        tmp = dest + ".part"
        last = None
        for attempt in range(5):
            try:
                h = hashlib.sha256()
                with self.open("blobs/" + digest) as r, open(tmp, "wb") as f:
                    while True:
                        b = r.read(1 << 20)
                        if not b:
                            break
                        h.update(b)
                        f.write(b)
                if h.hexdigest() != want:
                    raise RuntimeError("digest mismatch for %s" % digest)
                os.replace(tmp, dest)
                return "downloaded"
            except Exception as e:  # network hiccup or expired token: retry
                last = e
                print("  blob %s attempt %d failed: %s" % (digest[:19], attempt + 1, e), flush=True)
                self.token = None if isinstance(e, urllib.error.HTTPError) and e.code == 401 else self.token
                time.sleep(5 * (attempt + 1))
        raise last


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ----------------------------------------------------------------------------- layers
def resolve_in_root(root, rel, follow_last=False):
    """Host path of archive path `rel`, following symlinks as if `root` were '/'.
    '..' is clamped at the root and absolute link targets restart at the root, so
    the result is always inside `root`."""
    parts = [p for p in rel.replace("\\", "/").split("/") if p not in ("", ".")]
    cur, i, hops = [], 0, 0
    while i < len(parts):
        p = parts[i]
        if p == "..":
            if cur:
                cur.pop()
            i += 1
            continue
        cand = os.path.join(root, *cur, p)
        last = i == len(parts) - 1
        if os.path.islink(cand) and (follow_last or not last):
            hops += 1
            if hops > 40:
                raise OSError("too many symlink hops resolving %r" % rel)
            tgt = os.readlink(cand)
            if tgt.startswith("/"):
                cur = []
            parts = [q for q in tgt.split("/") if q not in ("", ".")] + parts[i + 1:]
            i = 0
            continue
        cur.append(p)
        i += 1
    return os.path.join(root, *cur)


def _rm(path):
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return
    if stat.S_ISDIR(st.st_mode):
        shutil.rmtree(path, ignore_errors=True)
    else:
        os.unlink(path)


def open_layer(path):
    with open(path, "rb") as f:
        magic = f.read(4)
    if magic[:2] == b"\x1f\x8b":
        return tarfile.open(path, "r|gz"), None
    if magic == b"\x28\xb5\x2f\xfd":
        import zstandard  # optional dependency, only for zstd layers
        fh = open(path, "rb")
        return tarfile.open(fileobj=zstandard.ZstdDecompressor().stream_reader(fh), mode="r|"), fh
    return tarfile.open(path, "r|"), None


def new_stats():
    return {k: 0 for k in ("files", "dirs", "symlinks", "hardlinks", "whiteouts", "opaque",
                           "skipped_dev", "skipped_bad", "errors")}


def apply_layer(tf, root, stats):
    """Apply one layer (an iterable tarfile) onto root."""
    root = os.path.abspath(root)
    dir_modes = []
    for m in tf:
        name = m.name.replace("\\", "/").rstrip("/")
        base, parent = os.path.basename(name), os.path.dirname(name)
        if not base or base in (".", ".."):
            stats["skipped_bad"] += 1
            continue
        try:
            if base == ".wh..wh..opq":
                d = resolve_in_root(root, parent, follow_last=True)
                if os.path.isdir(d) and not os.path.islink(d):
                    for e in os.listdir(d):
                        _rm(os.path.join(d, e))
                stats["opaque"] += 1
                continue
            if base.startswith(".wh."):
                _rm(os.path.join(resolve_in_root(root, parent, follow_last=True), base[4:]))
                stats["whiteouts"] += 1
                continue
            if m.isdev() or m.isfifo():
                stats["skipped_dev"] += 1
                continue
            pdir = resolve_in_root(root, parent, follow_last=True)
            dest = os.path.join(pdir, base)
            if os.path.commonpath([root, dest]) != root or dest == root:
                stats["skipped_bad"] += 1
                continue
            os.makedirs(pdir, exist_ok=True)
            if m.isdir():
                if os.path.lexists(dest) and not (os.path.isdir(dest) and not os.path.islink(dest)):
                    _rm(dest)
                os.makedirs(dest, exist_ok=True)
                dir_modes.append((dest, m.mode))
                stats["dirs"] += 1
                continue
            _rm(dest)
            if m.issym():
                os.symlink(m.linkname, dest)
                stats["symlinks"] += 1
            elif m.islnk():
                src = resolve_in_root(root, m.linkname, follow_last=False)
                try:
                    os.link(src, dest)
                except OSError:
                    shutil.copy2(src, dest)
                stats["hardlinks"] += 1
            elif m.isreg():
                src = tf.extractfile(m)
                with open(dest, "wb") as f:
                    shutil.copyfileobj(src, f, 1 << 20)
                os.chmod(dest, (m.mode & 0o777) | 0o600)
                try:
                    os.utime(dest, (m.mtime, m.mtime))
                except OSError:
                    pass
                stats["files"] += 1
            else:
                stats["skipped_bad"] += 1
        except Exception as e:
            stats["errors"] += 1
            if stats["errors"] <= 20:
                print("  layer entry %r: %s" % (m.name, e), flush=True)
    for d, mode in reversed(dir_modes):
        try:
            os.chmod(d, (mode & 0o777) | 0o700)
        except OSError:
            pass


def write_env(rootfs, config):
    """Write the image's ENV as a sourceable shell file /.ocipull-env.sh in the rootfs."""
    cfg = config.get("config") or {}
    lines = ["# written by ocipull %s from the image config" % VERSION]
    for kv in cfg.get("Env") or []:
        k, _, v = kv.partition("=")
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", k):
            lines.append("export %s=%s" % (k, shlex.quote(v)))
    with open(os.path.join(rootfs, ".ocipull-env.sh"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return cfg


def pull(image, rootfs, blobs, arch="amd64"):
    host, repo, ref = parse_ref(image)
    reg = Registry(host, repo)
    t0 = time.time()
    man, digest = reg.manifest(ref, arch)
    os.makedirs(blobs, exist_ok=True)
    stamp = os.path.join(rootfs, STAMP)
    summary = {"ocipull": VERSION, "image": image, "manifest_digest": digest,
               "layers": [], "reused": False}
    cdig = man["config"]["digest"]
    cpath = os.path.join(blobs, cdig.replace(":", "_"))
    reg.blob(cdig, cpath)
    with open(cpath) as f:
        config = json.load(f)
    if os.path.exists(stamp) and open(stamp).read().strip() == digest:
        summary["reused"] = True
        summary["config"] = config.get("config")
        summary["seconds"] = round(time.time() - t0, 1)
        return summary
    if os.path.exists(rootfs):
        shutil.rmtree(rootfs)
    os.makedirs(rootfs)
    stats = new_stats()
    for lay in man["layers"]:
        d = lay["digest"]
        p = os.path.join(blobs, d.replace(":", "_"))
        t1 = time.time()
        how = reg.blob(d, p)
        t2 = time.time()
        tf, fh = open_layer(p)
        try:
            apply_layer(tf, rootfs, stats)
        finally:
            tf.close()
            if fh:
                fh.close()
        info = {"digest": d, "bytes": lay.get("size"), "mediaType": lay.get("mediaType"),
                "fetch": how, "fetch_s": round(t2 - t1, 1), "apply_s": round(time.time() - t2, 1)}
        summary["layers"].append(info)
        print("  layer %s %s %.0f MB fetch %.0fs apply %.0fs" % (
            d[:19], how, (lay.get("size") or 0) / 1e6, info["fetch_s"], info["apply_s"]), flush=True)
        os.unlink(p)  # keep only the extracted root, not the compressed copy
    summary["stats"] = stats
    summary["config"] = write_env(rootfs, config)
    with open(stamp, "w") as f:
        f.write(digest + "\n")
    summary["seconds"] = round(time.time() - t0, 1)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("image")
    ap.add_argument("--rootfs", required=True)
    ap.add_argument("--blobs", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--arch", default="amd64")
    a = ap.parse_args(argv)
    try:
        s = pull(a.image, a.rootfs, a.blobs, a.arch)
        s["ok"] = True
    except Exception as e:
        s = {"ocipull": VERSION, "image": a.image, "ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    with open(a.summary, "w") as f:
        json.dump(s, f, indent=1)
    print("OCIPULL: ok=%s reused=%s layers=%d seconds=%s stats=%s error=%s" % (
        s.get("ok"), s.get("reused"), len(s.get("layers", [])), s.get("seconds"),
        json.dumps(s.get("stats")), s.get("error", "")), flush=True)
    return 0 if s["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
