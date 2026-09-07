import unittest

from llama.pylib import fix_ocr


class TestFixOcrMore(unittest.TestCase):
    # ---------------------------------------------------------------------
    def test_filter_lines_extra_01(self) -> None:
        # Lines containing filter words are removed (case-insensitive), others kept
        text = "Department of Botany\nPond near canal\nMuseum of Natural History\nMay 29, 1966"
        expect = "Pond near canal\nMay 29, 1966"
        assert fix_ocr.filter_lines(text) == expect

    def test_filter_lines_extra_02(self) -> None:
        # The pattern is word-bounded: "sciences" does not match "science"
        text = "science\nMolecular Sciences"
        expect = "science"
        assert fix_ocr.filter_lines(text) == expect

    def test_filter_lines_extra_03(self) -> None:
        # Result is stripped
        assert fix_ocr.filter_lines("  \nline\n  ") == "line"

    # ---------------------------------------------------------------------
    def test_fix_entities_extra_01(self) -> None:
        assert fix_ocr.fix_entities("a<br>b") == "a\nb"
        assert fix_ocr.fix_entities("a<br/>b") == "a\nb"

    def test_fix_entities_extra_02(self) -> None:
        assert fix_ocr.fix_entities("5 &lt; 10 &amp; 3 &gt; 1") == "5 < 10 & 3 > 1"

    def test_fix_entities_extra_03(self) -> None:
        # Decoding happens once, not recursively
        assert fix_ocr.fix_entities("&amp;lt;") == "&lt;"

    def test_fix_entities_extra_04(self) -> None:
        # Handle: "<br />" (space before the slash)
        assert fix_ocr.fix_entities("a<br />b") == "a\nb"

    # ---------------------------------------------------------------------
    def test_join_lines_extra_01(self) -> None:
        # A single break joins the lines
        assert fix_ocr.join_lines("line1\nline2") == "line1 line2"

    def test_join_lines_extra_02(self) -> None:
        # Two or more breaks are kept as a paragraph break
        assert fix_ocr.join_lines("line1\n\nline2") == "line1\n\nline2"

    def test_join_lines_extra_03(self) -> None:
        # Extra blank lines collapse to a single paragraph break
        assert fix_ocr.join_lines("line1\n\n\nline2") == "line1\n\nline2"

    def test_join_lines_extra_04(self) -> None:
        # Trailing newlines are stripped
        assert fix_ocr.join_lines("a\nb\n") == "a b"

    # ---------------------------------------------------------------------
    def test_remove_identical_lines_extra_01(self) -> None:
        # Deduplication is case-sensitive
        assert fix_ocr.remove_identical_lines("Line\nline\nx") == "Line\nline\nx"

    def test_remove_identical_lines_extra_02(self) -> None:
        # Space-only lines are kept (as blank lines) and their spaces stripped
        assert fix_ocr.remove_identical_lines("a\n   \nb\n   ") == "a\n\nb"

    # ---------------------------------------------------------------------
    def test_clean_ocr_01(self) -> None:
        # clean_ocr fixes entities
        assert fix_ocr.clean_ocr("a<br>b\na") == "a\nb\na"

    def test_clean_ocr_02(self) -> None:
        # Filter words are kept (filter_lines is not part of clean_ocr)
        assert fix_ocr.clean_ocr("Herbarium\nline") == "Herbarium\nline"

    # ---------------------------------------------------------------------
    def test_html_to_md_extra_01(self) -> None:
        # Bold / italic markdown notations are stripped
        assert fix_ocr.html_to_md("<b>bold</b> and <i>ital</i>") == "bold and ital"
        assert fix_ocr.html_to_md("<b>a</b> and <b>b</b>") == "a and b"

    def test_html_to_md_extra_02(self) -> None:
        # img tags are stripped
        assert fix_ocr.html_to_md('<img src="x.png">hello') == "hello"

    def test_html_to_md_extra_03(self) -> None:
        # Paragraphs are separated by a blank line
        assert (
            fix_ocr.html_to_md("<p>para one</p><p>para two</p>")
            == "para one\n\npara two"
        )

    def test_html_to_md_extra_04(self) -> None:
        # Remove tags
        assert fix_ocr.html_to_md("<i>state-wide</i>") == "state-wide"


if __name__ == "__main__":
    unittest.main()
