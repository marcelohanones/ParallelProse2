"""Dispatch by content (F5) and the readers for container.xml, content.opf and toc.ncx."""

import posixpath
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass

from parallelprose2.ingest.errors import IngestError

MIMETYPE = b"application/epub+zip"


@dataclass(frozen=True)
class Package:
    opf_dir: str  # directory of content.opf inside the zip; manifest hrefs are relative to it
    spine: tuple[str, ...]  # zip-root paths, in reading order
    navpoints: tuple[tuple[str, str], ...]  # (label, zip-root path) for top-level navPoints, in NCX order


def open_epub(path: str) -> zipfile.ZipFile:
    """Refuse anything whose content is not an epub; the extension is never consulted."""
    try:
        z = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        raise IngestError("E-INPUT-NOT-EPUB", path) from None
    try:
        if z.read("mimetype") != MIMETYPE or "META-INF/container.xml" not in z.namelist():
            raise IngestError("E-INPUT-NOT-EPUB", path)
    except KeyError:
        raise IngestError("E-INPUT-NOT-EPUB", path) from None
    return z


def read_package(z: zipfile.ZipFile) -> Package:
    container = ET.fromstring(z.read("META-INF/container.xml"))
    rootfile = container.find(".//{*}rootfile").get("full-path")
    opf_dir = posixpath.dirname(rootfile)
    opf = ET.fromstring(z.read(rootfile))

    manifest = {item.get("id"): item.get("href") for item in opf.find("{*}manifest")}
    spine_el = opf.find("{*}spine")
    spine = tuple(resolve_href(opf_dir, manifest[ref.get("idref")]) for ref in spine_el.findall("{*}itemref"))

    ncx_path = resolve_href(opf_dir, manifest[spine_el.get("toc")])
    ncx = ET.fromstring(z.read(ncx_path))
    ncx_dir = posixpath.dirname(ncx_path)
    navpoints = []
    for navpoint in ncx.find("{*}navMap").findall("{*}navPoint"):
        label = navpoint.find("{*}navLabel/{*}text").text.strip()
        src = navpoint.find("{*}content").get("src").split("#", 1)[0]
        navpoints.append((label, resolve_href(ncx_dir, src)))
    return Package(opf_dir=opf_dir, spine=spine, navpoints=tuple(navpoints))


def resolve_href(directory: str, href: str) -> str:
    return posixpath.normpath(posixpath.join(directory, href)) if directory else posixpath.normpath(href)
