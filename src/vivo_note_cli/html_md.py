from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser
from typing import Any, ClassVar


class VivoHTMLToMarkdown(HTMLParser):
    """Small dependency-free converter for vivo note HTML."""

    BLOCK_TAGS: ClassVar[set[str]] = {
        "address",
        "article",
        "blockquote",
        "div",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "p",
        "pre",
        "section",
        "table",
        "tr",
    }

    HEADING_LEVELS: ClassVar[dict[str, int]] = {f"h{level}": level for level in range(1, 7)}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.lists: list[dict[str, Any]] = []
        self.link_stack: list[str] = []

    def _newline(self) -> None:
        if self.parts and not self.parts[-1].endswith("\n"):
            self.parts.append("\n")

    def _blank_line(self) -> None:
        self._newline()
        if self.parts and self.parts[-1] != "\n\n":
            self.parts.append("\n")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {name.lower(): value for name, value in attrs if value is not None}
        if tag == "br":
            self.parts.append("\n")
        elif tag in self.HEADING_LEVELS:
            self._blank_line()
            self.parts.append("#" * self.HEADING_LEVELS[tag] + " ")
        elif tag in self.BLOCK_TAGS:
            self._blank_line()
        elif tag in {"ol", "ul"}:
            self._newline()
            self.lists.append({"tag": tag, "index": 0})
        elif tag == "li":
            self._newline()
            indent = "  " * max(0, len(self.lists) - 1)
            if self.lists and self.lists[-1]["tag"] == "ol":
                self.lists[-1]["index"] += 1
                marker = f"{self.lists[-1]['index']}. "
            else:
                marker = "- "
            self.parts.append(f"{indent}{marker}")
        elif tag == "a" and attr_map.get("href"):
            self.link_stack.append(attr_map["href"])
            self.parts.append("[")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "a" and self.link_stack:
            href = self.link_stack.pop()
            self.parts.append(f"]({href})")
        elif tag in self.HEADING_LEVELS or tag in self.BLOCK_TAGS or tag == "li":
            self._newline()
        elif tag in {"ol", "ul"}:
            if self.lists:
                self.lists.pop()
            self._newline()

    def handle_data(self, data: str) -> None:
        if data:
            self.parts.append(unescape(data))

    def markdown(self) -> str:
        text = "".join(self.parts).replace("\xa0", " ")
        lines: list[str] = []
        previous_blank = False
        for raw_line in text.splitlines():
            line = re.sub(r"[ \t]+", " ", raw_line).rstrip()
            blank = not line.strip()
            if blank and previous_blank:
                continue
            lines.append(line)
            previous_blank = blank
        return "\n".join(lines).strip()


def html_to_markdown(html: str | None) -> str:
    if not html:
        return ""
    parser = VivoHTMLToMarkdown()
    parser.feed(html)
    parser.close()
    return parser.markdown()
