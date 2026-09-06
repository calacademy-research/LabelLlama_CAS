import unittest

from llama.llm_fields.location.county import County


class TestCounty(unittest.TestCase):
    def test_county_01(self) -> None:
        # Trailing "County" label is removed
        assert County("", "Cameron County").county == "Cameron"

    def test_county_02(self) -> None:
        # Trailing "Co." / "co" labels are removed, case-insensitively
        assert County("", "Cameron Co.").county == "Cameron"
        assert County("", "Cameron co").county == "Cameron"

    def test_county_03(self) -> None:
        # A non-trailing label is left alone
        assert County("", "Cameron County, Texas").county == "Cameron County, Texas"

    def test_county_04(self) -> None:
        # Names that merely resemble the label are unchanged
        assert County("", "Canyon").county == "Canyon"
        assert County("", "Cameronco").county == "Cameronco"

    def test_county_05(self) -> None:
        # Empty inputs and empty-value notations stay empty
        assert County("", "").county == ""
        assert County("", "none").county == ""
