"""Identity (M5, M9, M12, M13): version_id and content_hash. Reads files; writes nothing.

version_id is one sha256 over the canonical serialization of the epub's bytes, the manifest's bytes, and every file under
src/parallelprose2/ (bytecode caches excluded: they are generated, not code). content_hash is the sha256 of the
canonical list of (name, sha256) pairs of the artifact's files, sorted by name.
"""

import hashlib
import json
import os

PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return sha256_bytes(f.read())


def source_files(root: str = PACKAGE_ROOT) -> list[list[str]]:
    """Every source file under root, as [relative path, sha256] pairs sorted by path."""
    pairs = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, name)
            pairs.append([os.path.relpath(full, root).replace(os.sep, "/"), sha256_file(full)])
    return sorted(pairs)


def version_id_of(epub: bytes, manifest: bytes, root: str = PACKAGE_ROOT) -> str:
    """version_id over the bytes of the two inputs and the source files (M5, M13). Canonical JSON, UTF-8."""
    return sha256_bytes(canonical({
        "epub": sha256_bytes(epub),
        "manifest": sha256_bytes(manifest),
        "source": source_files(root),
    }))


def version_id(epub_path: str, manifest_path: str, root: str = PACKAGE_ROOT) -> str:
    with open(epub_path, "rb") as f:
        epub = f.read()
    with open(manifest_path, "rb") as f:
        manifest = f.read()
    return version_id_of(epub, manifest, root)


def content_hash(files: dict[str, str]) -> str:
    return sha256_bytes(canonical(sorted(files.items())))
