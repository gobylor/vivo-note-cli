from vivo_note_cli.html_md import html_to_markdown


def test_converts_paragraphs_and_breaks() -> None:
    html = "<p>Hello<br>world</p><p>Next</p>"
    assert html_to_markdown(html) == "Hello\nworld\n\nNext"


def test_converts_lists() -> None:
    html = "<ol><li>one</li><li>two</li></ol><ul><li>a</li><li>b</li></ul>"
    assert html_to_markdown(html) == "1. one\n2. two\n- a\n- b"


def test_preserves_chinese_text() -> None:
    html = "<div>今天很开心&nbsp;😄</div><p>继续记录</p>"
    assert html_to_markdown(html) == "今天很开心 😄\n\n继续记录"


def test_converts_links() -> None:
    assert (
        html_to_markdown('<a href="https://example.com">link</a>') == "[link](https://example.com)"
    )
