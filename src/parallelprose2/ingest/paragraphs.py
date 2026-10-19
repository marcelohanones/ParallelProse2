"""Paragraph extraction for body files (D6, M14, M29). Reads the epub; writes nothing.

A paragraph is a leaf text run. Every element that is neither inline nor a heading is a block boundary (M29(2)): it
yields one paragraph per direct text run, and each child is processed the same way, in document order (M14). Inline
elements do not split a run. Headings are not text of the body. An empty <p> is dropped and listed; an empty wrapper is
dropped silently. Containers such as ul, ol and body pass their children through.
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from parallelprose2.ingest.check import check_inputs
from parallelprose2.ingest.epub import open_epub, read_package, resolve_href
from parallelprose2.ingest.inputs import Inputs
from parallelprose2.ingest.errors import IngestError
from parallelprose2.ingest.manifest import load_manifest

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
INLINE_TAGS = {"span", "em", "i", "b", "strong", "a", "small", "sup", "sub", "u", "font", "abbr", "cite", "code", "q", "img"}


@dataclass(frozen=True)
class Paragraph:
    index: int  # 1…N over kept paragraphs, in reading order
    href: str  # the body file it came from, zip-root path
    chapter: str  # the chapter's label, from the TOC
    chapter_seq: int  # position within the chapter, from 1
    text: str
    quoted: bool
    source: str | None
    printed_no: int | None = None  # D5: the h3.num that precedes the leaf block (Debord); None otherwise


@dataclass(frozen=True)
class Dropped:
    href: str
    position: int  # 1-based ordinal among the <p> elements of the file


@dataclass(frozen=True)
class Extraction:
    paragraphs: tuple[Paragraph, ...]
    dropped: tuple[Dropped, ...]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _local(tag: str) -> str:
    return tag.split("}")[-1]


def _inline_text(el: ET.Element) -> str:
    parts = [el.text or ""]
    for child in el:
        parts.append(" " if _local(child.tag) == "br" else _inline_text(child))
        parts.append(child.tail or "")
    return "".join(parts)


class _State:
    def __init__(self, href: str = ""):
        self.href = href  # the file being read, for the error locator
        self.p_count = 0  # <p> elements seen in the current file
        self.dropped: list[int] = []
        self.pending_number: int | None = None  # an h3.num waiting for its leaf block (D5)

    def take_number(self) -> int | None:
        number, self.pending_number = self.pending_number, None
        return number


def _collect(el, quoted, source, out, state, skip=frozenset()):
    """Append (text, quoted, source) for each paragraph under el, in document order."""
    buf: list[str] = []

    def flush():
        text = normalize("".join(buf))
        buf.clear()
        if text:
            out.append((text, quoted, source, state.take_number()))

    if el.text:
        buf.append(el.text)
    for child in list(el):
        tag = _local(child.tag)
        if id(child) in skip:
            state.p_count += 1  # an attribution is a <p> for position, and is never text of the body
        elif tag == "p":
            state.p_count += 1
            if not normalize(_inline_text(child)):
                state.dropped.append(state.p_count)
            else:
                flush()
                _collect(child, quoted, source, out, state)
        elif tag == "br":
            buf.append(" ")
        elif tag in INLINE_TAGS:
            buf.append(_inline_text(child))
        elif tag in HEADING_TAGS:
            if tag == "h3" and "num" in (child.get("class") or "").split():
                try:
                    state.pending_number = int(normalize(_inline_text(child)))
                except ValueError:  # M43: a printed number is an integer, or the book is malformed
                    raise IngestError("E-PRINTED-NUMBER-MALFORMED", state.href) from None
        elif tag == "blockquote":
            flush()
            attribution = [c for c in child if _local(c.tag) == "p" and "attrib" in (c.get("class") or "")]
            src = normalize(" ".join(_inline_text(a) for a in attribution)) or None
            _collect(child, True, src, out, state, skip={id(a) for a in attribution})
        else:  # div, li, and containers such as ul and ol
            flush()
            _collect(child, quoted, source, out, state)
        if child.tail:
            buf.append(child.tail)
    flush()


def _read_body(z, href):
    """The body element of a body file. A member the OPF names but the zip lacks is E-PACKAGE-MALFORMED (M27); a file
    that is not well-formed XHTML, or has no body, is E-XHTML-MALFORMED (M31)."""
    try:
        data = z.read(href)
    except KeyError:
        raise IngestError("E-PACKAGE-MALFORMED", href) from None
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        raise IngestError("E-XHTML-MALFORMED", href) from None
    body = next((el for el in root.iter() if _local(el.tag) == "body"), None)
    if body is None:
        raise IngestError("E-XHTML-MALFORMED", href)
    return body


def extract(epub_path: str, manifest_path: str) -> Extraction:
    return extract_inputs(Inputs.read(epub_path, manifest_path))


def extract_inputs(inp: Inputs) -> Extraction:
    """Run phases 1 and 2, then extract the paragraphs of every body file in spine order."""
    summary = check_inputs(inp)
    labels = {c.chapter: c.label for c in summary.chapters}
    manifest = load_manifest(inp.manifest, inp.manifest_path)
    with open_epub(inp.epub, inp.epub_path) as z:
        package = read_package(z)
        entries = {resolve_href(package.opf_dir, e.href): e for e in manifest.spine}
        paragraphs: list[Paragraph] = []
        dropped: list[Dropped] = []
        seq: dict[str, int] = {}
        for href in package.spine:
            entry = entries[href]
            if entry.cls != "body":
                continue
            body = _read_body(z, href)
            out: list[tuple[str, bool, str | None, int | None]] = []
            state = _State(href)
            _collect(body, False, None, out, state)
            for position in state.dropped:
                dropped.append(Dropped(href=href, position=position))
            for text, quoted, source, printed_no in out:
                seq[entry.chapter] = seq.get(entry.chapter, 0) + 1
                paragraphs.append(
                    Paragraph(
                        index=len(paragraphs) + 1,
                        href=href,
                        chapter=labels[entry.chapter],
                        chapter_seq=seq[entry.chapter],
                        text=text,
                        quoted=quoted,
                        source=source,
                        printed_no=printed_no,
                    )
                )
    return Extraction(paragraphs=tuple(paragraphs), dropped=tuple(dropped))
