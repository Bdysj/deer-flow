"""``find_grep_matches`` must not match a regex against the line terminator.

Lines came straight from iterating the file, so each still ended in ``\\n``.
That newline satisfied ``[^;]``, ``\\s`` and similar classes right before
``$``, so "lines not ending in ;" or "trailing whitespace" searches returned
every line, unlike ``grep -E`` (which the remote providers shell out to).
"""

from pathlib import Path

import pytest

from deerflow.sandbox.search import find_grep_matches

CONTENT = "const a = 1;\nconst b = 2\nclean line\ntrailing space \nlast;"


@pytest.mark.parametrize(
    ("pattern", "expected_lines"),
    [
        (r"[^;]$", [2, 3, 4]),
        (r"\s$", [4]),
        (r";$", [1, 5]),
        (r"^clean line$", [3]),
    ],
)
def test_line_end_anchor_ignores_the_newline(tmp_path: Path, pattern: str, expected_lines: list[int]) -> None:
    (tmp_path / "code.js").write_text(CONTENT, encoding="utf-8")

    matches, truncated = find_grep_matches(tmp_path, pattern)

    assert [m.line_number for m in matches] == expected_lines
    assert truncated is False


def test_crlf_file_is_matched_without_its_line_terminator(tmp_path: Path) -> None:
    (tmp_path / "code.js").write_bytes(b"const a = 1;\r\nconst b = 2\r\n")

    matches, _ = find_grep_matches(tmp_path, r"[^;]$")

    assert [m.line_number for m in matches] == [2]
