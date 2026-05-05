from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

# Block delimiter lines (must consist solely of these chars, length >= 4) that open
# and close a "verbatim" region in which lines starting with `=` MUST NOT be parsed
# as headings or attributes. Pairs of identical delimiters open and close.
_BLOCK_DELIMS: frozenset[str] = frozenset(("----", "....", "++++", "****", "____", "===="))
_COMMENT_DELIM = "////"

_ATTR_RE = re.compile(r"^:(?P<name>!?[A-Za-z0-9_][A-Za-z0-9_-]*)(?:!)?:\s*(?P<value>.*?)\s*$")
_HEADING_RE = re.compile(r"^(?P<eq>=+)\s+(?P<text>.+?)\s*$")


@dataclass
class AsciidocDocument:
    """
    Parsed AsciiDoc document. `headings` maps the heading level (1 = `==`,
    2 = `===`, ...) to the ordered list of heading texts at that level.
    `h0` is the single document title (`= ...`) if present.
    `author` is the raw author line as it appears below the document title.
    `attributes` collects all document/inline `:name: value` attribute entries.
    Convenience properties `h1` through `h6` return the lists for the most
    common levels; use `headings.get(level, [])` for arbitrary depths.
    """

    file_name: str
    file_location: Path
    h0: str | None = None
    author: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)
    headings: dict[int, list[str]] = field(default_factory=dict)

    @property
    def h1(self) -> list[str]:
        return self.headings.get(1, [])

    @property
    def h2(self) -> list[str]:
        return self.headings.get(2, [])

    @property
    def h3(self) -> list[str]:
        return self.headings.get(3, [])

    @property
    def h4(self) -> list[str]:
        return self.headings.get(4, [])

    @property
    def h5(self) -> list[str]:
        return self.headings.get(5, [])

    @property
    def h6(self) -> list[str]:
        return self.headings.get(6, [])

    def to_json(self, *, indent: int | None = None) -> str:
        """
        Serialise the document to a JSON string. `file_location` is rendered
        as its POSIX string form and `headings` keys are stringified, since
        JSON object keys must be strings.
        """
        payload: dict[str, object] = {
            "file_name": self.file_name,
            "file_location": str(self.file_location),
            "h0": self.h0,
            "author": self.author,
            "attributes": self.attributes,
            "headings": {str(level): texts for level, texts in self.headings.items()},
        }
        return json.dumps(payload, indent=indent, ensure_ascii=False)


def _is_block_delim(line: str) -> str | None:
    s = line.rstrip()
    if len(s) < 4:
        return None
    if s == _COMMENT_DELIM or s.startswith(_COMMENT_DELIM) and set(s) == {"/"}:
        return _COMMENT_DELIM
    for d in _BLOCK_DELIMS:
        # Require an exact run of the delimiter character of length >= 4.
        if set(s) == {d[0]} and len(s) >= 4:
            return d[0] * 4
    return None


def parse_asciidoc(path: str | Path) -> AsciidocDocument:
    """
    Parse an AsciiDoc file at `path` into an `AsciidocDocument`.

    Recognises the document title (`= ...`) as `h0`, the optional author line
    immediately following it, AsciiDoc attribute entries (`:name: value`) and
    section headings (`==`, `===`, ...) outside of verbatim/comment blocks.
    The parser is intentionally permissive: malformed sections are ignored
    rather than raising, so a partial parse is preferred over a hard failure.
    """
    location = Path(path)
    text = location.read_text(encoding="utf-8")

    doc = AsciidocDocument(file_name=location.name, file_location=location.resolve())

    open_block: str | None = None
    seen_h0 = False
    expect_author = False

    for raw in text.splitlines():
        # Block delimiter handling: toggle in/out of verbatim regions where
        # `=` lines and `:attr:` lines must not be parsed.
        delim = _is_block_delim(raw)
        if delim is not None:
            if open_block is None:
                open_block = delim
            elif open_block == delim:
                open_block = None
            # Either way, the delimiter line itself is not content.
            expect_author = False
            continue

        if open_block is not None:
            expect_author = False
            continue

        line = raw.rstrip()

        # Line comments are skipped without consuming the author-slot signal.
        if line.startswith("//") and not line.startswith("///"):
            continue

        # Heading line.
        m = _HEADING_RE.match(line)
        if m:
            level = len(m.group("eq")) - 1  # `==` -> 1, `===` -> 2, ...
            text_part = m.group("text")
            if level == 0:
                if not seen_h0:
                    doc.h0 = text_part
                    seen_h0 = True
                    expect_author = True
                # Stray additional level-0 lines are recorded under level 0 too.
                else:
                    doc.headings.setdefault(0, []).append(text_part)
                    expect_author = False
                continue
            doc.headings.setdefault(level, []).append(text_part)
            expect_author = False
            continue

        # Attribute entry.
        am = _ATTR_RE.match(line)
        if am:
            name = am.group("name")
            value = am.group("value")
            if name.startswith("!"):
                # `:!name:` unsets — record empty for visibility.
                doc.attributes[name[1:]] = ""
            else:
                doc.attributes[name] = value
            expect_author = False
            continue

        # Author line: first non-empty, non-attribute, non-heading, non-comment
        # line directly after the document title.
        if expect_author:
            if line.strip():
                doc.author = line.strip()
                expect_author = False
            # Blank lines between title and author are tolerated.
            continue

    return doc
