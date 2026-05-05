from __future__ import annotations

import json
import tempfile
from pathlib import Path
from textwrap import dedent

from dracklib.asciidoc import parse_asciidoc


def _write_tmp(name: str, content: str) -> Path:
    tmp_dir = Path(tempfile.mkdtemp(prefix="dracklib-asciidoc-"))
    p = tmp_dir / name
    p.write_text(content, encoding="utf-8")
    return p


def test_parse_asciidoc_full() -> None:
    src = dedent(
        """
        = My Document Title
        Daniel Drack <daniel@example.com>
        :toc:
        :revnumber: 1.2.3
        :author-affiliation: Example Inc.

        == First Section
        Some text.

        === Subsection
        ==== Deeper

        == Second Section

        ----
        == not-a-heading-inside-listing
        :not-an-attribute: value
        ----

        // line comment, not a heading: == nope

        ===== Five
        """
    ).strip()

    path = _write_tmp("doc.adoc", src)
    doc = parse_asciidoc(path)

    assert doc.file_name == "doc.adoc"
    assert doc.file_location == path.resolve()
    assert doc.h0 == "My Document Title"
    assert doc.author == "Daniel Drack <daniel@example.com>"
    assert doc.attributes["toc"] == ""
    assert doc.attributes["revnumber"] == "1.2.3"
    assert doc.attributes["author-affiliation"] == "Example Inc."
    assert "not-an-attribute" not in doc.attributes
    assert doc.h1 == ["First Section", "Second Section"]
    assert doc.h2 == ["Subsection"]
    assert doc.h3 == ["Deeper"]
    assert doc.headings.get(4) == ["Five"]


def test_parse_asciidoc_no_author_no_attrs() -> None:
    src = dedent(
        """
        = Title Only

        == Only Section
        """
    ).strip()
    path = _write_tmp("min.adoc", src)
    doc = parse_asciidoc(path)
    assert doc.h0 == "Title Only"
    assert doc.author is None
    assert doc.attributes == {}
    assert doc.h1 == ["Only Section"]


def test_parse_asciidoc_unset_attribute() -> None:
    src = dedent(
        """
        = T
        :foo: bar
        :!foo:
        """
    ).strip()
    path = _write_tmp("u.adoc", src)
    doc = parse_asciidoc(path)
    assert doc.attributes["foo"] == ""


def test_to_json_round_trip() -> None:
    src = dedent(
        """
        = JSON Doc
        Jane Doe <jane@example.com>
        :rev: 9

        == One
        === Deep
        """
    ).strip()
    path = _write_tmp("j.adoc", src)
    doc = parse_asciidoc(path)
    payload = json.loads(doc.to_json())

    assert payload["file_name"] == "j.adoc"
    assert payload["file_location"] == str(path.resolve())
    assert payload["h0"] == "JSON Doc"
    assert payload["author"] == "Jane Doe <jane@example.com>"
    assert payload["attributes"] == {"rev": "9"}
    assert payload["headings"] == {"1": ["One"], "2": ["Deep"]}
