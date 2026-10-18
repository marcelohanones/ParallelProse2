"""Dispatch by content (F5) and the readers for container.xml, content.opf and toc.ncx."""

import posixpath
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from urllib.parse import unquote

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
    except FileNotFoundError:
        raise IngestError("E-INPUT-MISSING", path) from None
    except zipfile.BadZipFile:
        raise IngestError("E-INPUT-NOT-EPUB", path) from None
    try:
        if z.read("mimetype") != MIMETYPE or "META-INF/container.xml" not in z.namelist():
            raise IngestError("E-INPUT-NOT-EPUB", path)
    except KeyError:
        raise IngestError("E-INPUT-NOT-EPUB", path) from None
    return z


def read_package(z: zipfile.ZipFile) -> Package:
    """Read the package. A member that is missing, or not a well-formed package element, stops as E-PACKAGE-MALFORMED."""
    container_name = "META-INF/container.xml"
    container = _parse(z, container_name)
    rootfile_el = container.find(".//{*}rootfile")
    rootfile = rootfile_el.get("full-path") if rootfile_el is not None else None
    if not rootfile:
        raise IngestError("E-PACKAGE-MALFORMED", container_name)
    opf_dir = posixpath.dirname(rootfile)
    opf = _parse(z, rootfile)

    manifest_el = opf.find("{*}manifest")
    spine_el = opf.find("{*}spine")
    if manifest_el is None or spine_el is None or not spine_el.get("toc"):
        raise IngestError("E-PACKAGE-MALFORMED", rootfile)
    manifest = {}
    for item in manifest_el.findall("{*}item"):
        if item.get("id") is None or item.get("href") is None:
            raise IngestError("E-PACKAGE-MALFORMED", rootfile)
        manifest[item.get("id")] = item.get("href")
    spine = []
    for ref in spine_el.findall("{*}itemref"):
        href = manifest.get(ref.get("idref"))
        if href is None:
            raise IngestError("E-PACKAGE-MALFORMED", rootfile)
        spine.append(resolve_href(opf_dir, href))
    ncx_href = manifest.get(spine_el.get("toc"))
    if ncx_href is None:
        raise IngestError("E-PACKAGE-MALFORMED", rootfile)

    ncx_path = resolve_href(opf_dir, ncx_href)
    ncx = _parse(z, ncx_path)
    nav_map = ncx.find("{*}navMap")
    if nav_map is None:
        raise IngestError("E-PACKAGE-MALFORMED", ncx_path)
    ncx_dir = posixpath.dirname(ncx_path)
    navpoints = []
    for navpoint in nav_map.findall("{*}navPoint"):
        label_el = navpoint.find("{*}navLabel/{*}text")
        content_el = navpoint.find("{*}content")
        if label_el is None or label_el.text is None or content_el is None or content_el.get("src") is None:
            raise IngestError("E-PACKAGE-MALFORMED", ncx_path)
        src = content_el.get("src").split("#", 1)[0]
        navpoints.append((label_el.text.strip(), resolve_href(ncx_dir, src)))
    return Package(opf_dir=opf_dir, spine=tuple(spine), navpoints=tuple(navpoints))


def _parse(z: zipfile.ZipFile, name: str) -> ET.Element:
    try:
        data = z.read(name)
    except KeyError:
        raise IngestError("E-PACKAGE-MALFORMED", name) from None
    try:
        return ET.fromstring(data)
    except ET.ParseError:
        raise IngestError("E-PACKAGE-MALFORMED", name) from None


def resolve_href(directory: str, href: str) -> str:
    """An href is a URI reference: percent-escapes are decoded, so it names the zip member."""
    href = unquote(href)
    return posixpath.normpath(posixpath.join(directory, href)) if directory else posixpath.normpath(href)
