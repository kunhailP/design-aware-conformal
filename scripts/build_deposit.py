"""Build the replication deposit: a curated, deterministic archive.

Assembles dist/dapcb-replication-<version>/ and zips it with a fixed file
order and fixed timestamps, so that rebuilding the deposit from the same
commit yields byte-identical archives. Writes a SHA256SUMS manifest of every
shipped file (also included inside the archive).

Included : REPLICATION.md (as the archive's top-level README alongside the
           repo README), LICENSE, CITATION.cff, requirements/pyproject/
           Makefile, pcb/, tests/, rpkg/, results/, configs/, docs/,
           paper/ (sources, bibliography, figures, compiled PDFs).
Excluded : data/ (licensed microdata; retrieval per docs/DATA_SOURCES.md),
           .git, caches, dist/, generated figures/ at repo root (tracked
           copies live in paper/figures/), editor droppings.

Run:  python scripts/build_deposit.py   (or: make deposit)
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INCLUDE = [
    "REPLICATION.md", "README.md", "LICENSE", "CITATION.cff",
    "requirements.txt", "pyproject.toml", "Makefile",
    "setup.sh", "run_public.sh", "run_restricted.sh", "run_all.sh",
    "pcb", "tests", "rpkg", "results", "configs", "docs", "paper", "scripts",
]
# NOTE: the licensed /data/ tree is never walked (it is not in INCLUDE);
# excluding the *name* "data" here would also drop the pcb/data loader
# package, which a replication analyst needs for Tier 2.
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git", "dist"}
EXCLUDE_SUFFIX = (".pyc", ".aux", ".bbl", ".blg", ".log", ".out", ".toc",
                  ".DS_Store")
# a fixed timestamp (the repo's public-release convention): 2026-08-20 00:00
ZIP_DATE = (2026, 8, 20, 0, 0, 0)


def _version() -> str:
    try:
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                           capture_output=True, text=True, check=True)
        return h.stdout.strip()
    except Exception:
        return "local"


def _files():
    out = []
    for top in INCLUDE:
        p = os.path.join(ROOT, top)
        if os.path.isfile(p):
            out.append(top)
            continue
        for dirpath, dirnames, filenames in os.walk(p):
            dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
            for f in sorted(filenames):
                if f.endswith(EXCLUDE_SUFFIX):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
                out.append(rel)
    return sorted(set(out))


def main():
    ver = _version()
    name = f"dapcb-replication-{ver}"
    dist = os.path.join(ROOT, "dist")
    os.makedirs(dist, exist_ok=True)

    files = _files()
    manifest = []
    for rel in files:
        with open(os.path.join(ROOT, rel), "rb") as fh:
            manifest.append((hashlib.sha256(fh.read()).hexdigest(), rel))
    man_path = os.path.join(dist, "SHA256SUMS")
    with open(man_path, "w") as fh:
        for digest, rel in manifest:
            fh.write(f"{digest}  {name}/{rel}\n")

    def _write_zip(path):
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            info = zipfile.ZipInfo(f"{name}/SHA256SUMS", date_time=ZIP_DATE)
            info.external_attr = 0o644 << 16
            z.writestr(info, open(man_path).read())
            for rel in files:
                info = zipfile.ZipInfo(f"{name}/{rel}", date_time=ZIP_DATE)
                info.external_attr = 0o644 << 16
                with open(os.path.join(ROOT, rel), "rb") as fh:
                    z.writestr(info, fh.read())
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()

    zpath = os.path.join(dist, f"{name}.zip")
    zdig = _write_zip(zpath)
    sz = os.path.getsize(zpath) / 1e6
    print(f"deposit : dist/{name}.zip  ({sz:.1f} MB, {len(files)} files)")
    print(f"sha256  : {zdig}")
    print(f"manifest: dist/SHA256SUMS")
    # determinism check: build the archive a second time and compare digests
    tmp = zpath + ".check"
    zdig2 = _write_zip(tmp)
    os.remove(tmp)
    if zdig2 != zdig:
        raise SystemExit("deposit archive is not deterministic: second build differs")
    print("deterministic: a second build of the same tree reproduced this sha256")


if __name__ == "__main__":
    main()
